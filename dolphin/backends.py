import json

import requests
from nanohttp import settings, HTTPForbidden
from restfulpy.logging_ import get_logger

from .exceptions import ChatServerNotFound, ChatServerNotAvailable, \
    ChatInternallError, ChatRoomNotFound, RoomMemberAlreadyExist, \
    RoomMemberNotFound


logger = get_logger('backends')


class CASClient:

    def __init__(self):
        self._server_name = self.__class__.__name__.replace('Client', '')

    def get_access_token(self, authorization_code):

        if authorization_code is None:
            raise HTTPForbidden()

        url = f'{settings.oauth.url}/apiv1/accesstokens'
        response = requests.request(
            'CREATE',
            url,
            data=dict(
                code=authorization_code,
                secret=settings.oauth['secret'],
                applicationId=settings.oauth['application_id']
            )
        )
        logger.debug(
            f'CREATE {url} - ' \
            f'authorizationCode="{authorization_code}" - ' \
            f'secret={settings.oauth["secret"]} - ' \
            f'applicationId={settings.oauth["application_id"]} - ' \
            f'response-HTTP-code={response.status_code} - ' \
            f'target-application={self._server_name}'
        )
        if response.status_code != 200:
            raise HTTPForbidden()

        result = json.loads(response.text)
        return result['accessToken'], result['memberId']

    def get_member(self, access_token):

        url = f'{settings.oauth.url}/apiv1/members/me'
        response = requests.get(
            url,
            headers={'authorization': f'oauth2-accesstoken {access_token}'}
        )
        logger.debug(f'GET {url}')
        if response.status_code != 200:
            raise HTTPForbidden()

        return json.loads(response.text)


class ChatClient:
    def __init__(self):
        self._server_name = self.__class__.__name__.replace('Client', '')

    def create_room(self, title, token, x_access_token, owner_id=None):
        url = f'{settings.chat.url}/apiv1/rooms'
        try:
            response = requests.request(
                'CREATE',
                url,
                data={'title':title},
                headers={
                    'authorization': token,
                    'X-Oauth2-Access-Token': x_access_token
                }
            )
            logger.debug(
                f'CREATE {url} - ' \
                f'title="{title}" - ' \
                f'response-HTTP-code={response.status_code} - ' \
                f'target-application={self._server_name}'
            )
            if response.status_code == 404:
                raise ChatServerNotFound()

            if response.status_code == 503:
                raise ChatServerNotAvailable()

            if response.status_code == 615:
                response = requests.request(
                    'LIST',
                    url,
                    headers={
                        'authorization': token,
                        'X-Oauth2-Access-Token': x_access_token
                    },
                    params={'title':title, 'ownerId':owner_id}
                )
                logger.debug(
                    f'LIST {url}?title={title}&ownerId={owner_id} - ' \
                    f'response-HTTP-code={response.status_code} - ' \
                    f'target-application={self._server_name}'
                )
                try:
                    rooms = json.loads(response.text)
                except ValueError:
                    raise ChatInternallError()

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

# TODO: This API is not implemented in Jaguar yet
#    def delete_room(self, id, token, x_access_token):
#
#        url = f'{settings.chat.url}/apiv1/rooms/{id}'
#        logger.debug(f'DELETE {url}')
#        response = requests.request(
#            'DELETE',
#            url,
#            headers={
#                'authorization': token,
#                'X-Oauth2-Access-Token': x_access_token
#            }
#        )
#        return response

    def add_member(self, id, user_id, token, x_access_token):

        url = f'{settings.chat.url}/apiv1/rooms/{id}'
        try:
            response = requests.request(
                'ADD',
                url,
                data={'userId': user_id},
                headers={
                    'authorization': token,
                    'X-Oauth2-Access-Token': x_access_token
                }
            )
            logger.debug(
                f'ADD {url} - ' \
                f'userId={user_id} - ' \
                f'response-HTTP-code={response.status_code} - ' \
                f'target-application={self._server_name}'
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

    def remove_member(self, id, user_id, token, x_access_token):

        url = f'{settings.chat.url}/apiv1/rooms/{id}'
        try:
            response = requests.request(
                'REMOVE',
                url,
                data={'userId':user_id},
                headers={'X-Oauth2-Access-Token':x_access_token}
            )
            logger.debug(
                f'REMOVE {url} - ' \
                f'userId={user_id} - ' \
                f'response-HTTP-code={response.status_code} - ' \
                f'target-application={self._server_name}'
            )
            if response.status_code == 404:
                raise ChatServerNotFound()

            # 502: Bad Gateway
            # 503: Service Unavailbale
            if response.status_code in (502, 503):
                raise ChatServerNotAvailable()

            # 611: User Not Found
            # Carrene/jaguar#13
            if response.status_code == 611:
                raise RoomMemberNotFound()

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

