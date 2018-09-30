import json

import requests
from nanohttp import settings, HTTPForbidden
from restfulpy.logging_ import get_logger

from .exceptions import ChatServerNotFound, ChatServerNotAvailable, \
    ChatInternallError, ChatRoomNotFound, RoomMemberAlreadyExist


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

    def create_room(self, title, access_token, owner_id=None):
        try:
            response = requests.request(
                'CREATE',
                f'{settings.chat.room.url}/apiv1/rooms',
                data={'title':title},
                headers={'X-Access-Token':access_token}
            )
            if response.status_code == 404:
                raise ChatServerNotFound()

            if response.status_code == 503:
                raise ChatServerNotAvailable()

            if response.status_code == 615:
                response = requests.request(
                    'LIST',
                    f'{settings.chat.room.url}/apiv1/rooms',
                    headers={'X-Access-Token':access_token},
                    params={'title':title, 'ownerId':owner_id}
                )
                rooms = json.loads(response.text)
                if len(rooms) == 1:
                    return rooms[0]

                raise ChatRoomNotFound()

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
            f'{settings.chat.room.url}/apiv1/rooms/{id}',
            headers={'X-Access-Token':access_token}
        )
        return response

    def add_member(self, id, user_id, access_token):

        try:
            response = requests.request(
                'ADD',
                f'{settings.chat.room.url}/apiv1/rooms/{id}',
                data={'userId':user_id},
                headers={'X-Access-Token':access_token}
            )
            if response.status_code == 404:
                raise ChatServerNotFound()

            # 502: Bad Gateway
            # 503: Service Unavailbale
            if response.status_code in (502, 503):
                raise ChatServerNotAvailable()

            # 604: Already Added To Target
            # Carrene/jaguar#3
            if response.status_code == 604:
                raise RoomMemberAlreadyExist()

            if response.status_code != 200:
                logger.exception(response.content.decode())
                raise ChatInternallError()

        except requests.RequestException as e: # pragma: no cover
            logger.exception(e)
            raise ChatInternallError()
        else:
            room = json.loads(response.text)
            return room

    def remove_member(self, id, user_id, access_token):

        response = requests.request(
            'REMOVE',
            f'{settings.chat.room.url}/apiv1/rooms/{id}',
            data={'userId':user_id},
            headers={'X-Access-Token':access_token}
        )
        room = json.loads(response.text)
        return room

