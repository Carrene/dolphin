import json

import requests
from nanohttp import settings, HTTPForbidden, HTTPUnauthorized, context
from restfulpy import logger

from .exceptions import *


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
        if response.status_code == 404:
            raise StatusCASServerNotFound()

        if response.status_code == 503:
            raise StatusCASServerNotAvailable()

        if response.status_code == 605:
            raise StatusInvalidApplicationID()

        if response.status_code == 608:
            raise StatusInvalidSecret()

        if response.status_code in (609, 610):
            raise HTTPUnauthorized

        if response.status_code != 200:
            logger.error(response.content.decode())
            raise StatusCASServerInternalError()

        result = json.loads(response.text)
        return result['accessToken'], result['memberId']

    def get_member(self, access_token):

        url = f'{settings.oauth.url}/apiv1/members/me'
        response = requests.get(
            url,
            headers={'authorization': f'oauth2-accesstoken {access_token}'}
        )
        logger.debug(
            f'GET {url} - ' \
            f'target-application={self._server_name}'
        )

        if response.status_code != 200:
            raise HTTPUnauthorized()

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
                data={'title': title},
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
                raise StatusChatServerNotFound()

            if response.status_code == 503:
                raise StatusChatServerNotAvailable()

            if response.status_code == 615:
                response = requests.request(
                    'LIST',
                    url,
                    headers={
                        'authorization': token,
                        'X-Oauth2-Access-Token': x_access_token
                    },
                    params={'title': title, 'ownerId': owner_id}
                )
                logger.debug(
                    f'LIST {url}?title={title}&ownerId={owner_id} - ' \
                    f'response-HTTP-code={response.status_code} - ' \
                    f'target-application={self._server_name}'
                )
                try:
                    rooms = json.loads(response.text)
                except ValueError:
                    raise StatusChatInternallError()

                if len(rooms) == 1:
                    return rooms[0]

                raise StatusChatRoomNotFound()

            if response.status_code != 200:
                logger.error(response.content.decode())
                raise StatusChatInternallError()

        except requests.RequestException as e: # pragma: no cover
            logger.error(e)
            raise StatusChatInternallError()

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
                raise StatusChatServerNotFound()

            # 502: Bad Gateway
            # 503: Service Unavailbale
            if response.status_code in (502, 503):
                raise StatusChatServerNotAvailable()

            # 604: Already Added To Target
            # Carrene/jaguar#3
            if response.status_code == 604:
                raise StatusRoomMemberAlreadyExist()

            if response.status_code != 200:
                logger.error(response.content.decode())
                raise StatusChatInternallError()

        except requests.RequestException as e: # pragma: no cover
            logger.error(e)
            raise StatusChatInternallError()

        else:
            room = json.loads(response.text)
            return room

    def kick_member(self, id, member_id, token, x_access_token):

        url = f'{settings.chat.url}/apiv1/rooms/{id}'
        try:
            response = requests.request(
                'KICK',
                url,
                data={'memberId': member_id},
                headers={
                    'authorization': token,
                    'X-Oauth2-Access-Token': x_access_token
                }
            )
            logger.debug(
                f'KICK {url} - ' \
                f'memberId={member_id} - ' \
                f'response-HTTP-code={response.status_code} - ' \
                f'target-application={self._server_name}'
            )
            if response.status_code == 404:
                raise StatusChatServerNotFound()

            # 502: Bad Gateway
            # 503: Service Unavailbale
            if response.status_code in (502, 503):
                raise StatusChatServerNotAvailable()

            # 611: User Not Found
            # Carrene/jaguar#13
            if response.status_code == 611:
                raise StatusRoomMemberNotFound()

            # 604: Already Added To Target
            # Carrene/jaguar#3
            if response.status_code == 604:
                raise StatusRoomMemberAlreadyExist()

            if response.status_code != 200:
                logger.error(response.content.decode())
                raise StatusChatInternallError()

        except requests.RequestException as e: # pragma: no cover
            logger.error(e)
            raise StatusChatInternallError()

        else:
            room = json.loads(response.text)
            return room

    def ensure_member(self, token, x_access_token):
        url = f'{settings.chat.url}/apiv1/members'
        try:
            response = requests.request(
                'ENSURE',
                url,
                headers={
                    'authorization': token,
                    'X-Oauth2-Access-Token': x_access_token
                }
            )
            logger.debug(
                f'ENSURE {url} - ' \
                f'response-HTTP-code={response.status_code} - ' \
                f'target-application={self._server_name}'
            )
            if response.status_code == 404:
                raise StatusChatServerNotFound()

            # 502: Bad Gateway
            # 503: Service Unavailbale
            if response.status_code in (502, 503):
                raise StatusChatServerNotAvailable()

            if response.status_code != 200:
                logger.error(response.content.decode())
                raise StatusChatInternallError()

        except requests.RequestException as e: # pragma: no cover
            logger.error(e)
            raise StatusChatInternallError()

        else:
            member = json.loads(response.text)
            return member

    def send_message(self, room_id, body, mimetype, token, x_access_token):

        url = f'{settings.chat.url}/apiv1/targets/{room_id}/messages'
        data = dict(body=body, mimetype=mimetype)
        try:
            response = requests.request(
                'SEND',
                url,
                json=data,
                headers={
                    'authorization': token,
                    'X-Oauth2-Access-Token': x_access_token,
                    'content-type': 'application/json',
                }
            )
            logger.debug(
                f'SEND {url} - ' \
                f'response-HTTP-code={response.status_code} - ' \
                f'target-application={self._server_name}'
            )
            if response.status_code == 404:
                raise StatusChatServerNotFound()

            # 502: Bad Gateway
            # 503: Service Unavailbale
            if response.status_code in (502, 503):
                raise StatusChatServerNotAvailable()

            if response.status_code != 200:
                logger.error(response.content.decode())
                raise StatusChatInternallError()

            member = json.loads(response.text)
            return member

        except requests.RequestException as e: # pragma: no cover
            logger.error(e)
            raise StatusChatInternallError()

