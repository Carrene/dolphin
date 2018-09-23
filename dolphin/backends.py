import json

import requests
from nanohttp import settings, HTTPForbidden
from restfulpy.logging_ import get_logger

from .exceptions import ChatServerNotFound, ChatServerNotAvailable, \
    ChatInternallError


logger = get_logger()


class CASClient:

    def get_access_token(self, authorization_code):

        if authorization_code is None:
            raise HTTPForbidden()

        response = requests.request(
            'CREATE',
            settings.oauth.access_token.url,
            data=dict(
                code=authorization_code,
                secret=settings.oauth['secret'],
                applicationId=settings.oauth['application_id']
            )
        )
        if response.status_code != 200:
            raise HTTPForbidden()

        result = json.loads(response.text)
        return result['accessToken'], result['memberId']

    def get_member(self, member_id, access_token):

        response = requests.get(
            f'{settings.oauth.member.url}/{member_id}',
            headers={'authorization': f'oauth2-accesstoken {access_token}'}
        )
        if response.status_code != 200:
            raise HTTPForbidden()

        return json.loads(response.text)


class ChatClient:

    def create_room(self, title, access_token):

        try:
            response = requests.request(
                'CREATE',
                f'{settings.chat.room.url}/rooms',
                data=dict(title=title),
                headers=dict(access_token=access_token)
            )
            if response.status_code == 404:
                raise ChatServerNotFound()

            if response.status_code == 503:
                raise ChatServerNotAvailable()

            if response.status_code != 200:
                logger.exception(response.content.decode())
                raise ChatInternallError()

        except requests.RequestException as e: # pragma: no cover
            logger.exception(e)
            raise ChatInternallError()
        else:
            room = json.loads(response.text)
            return room

    def delete_room(self, id, access_token):

        response = requests.request(
            'DELETE',
            f'{settings.chat.room.url}/rooms/{id}',
            headers=dict(access_token=access_token)
        )

