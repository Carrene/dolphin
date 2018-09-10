import urllib
import json

import requests
from nanohttp import settings, HTTPFound, HTTPForbidden


class CASClient:

    def get_access_token(self, authorization_code):

        if authorization_code is None:
            raise HTTPForbidden()
        cas_access_token = requests.request(
            'CREATE',
            settings.oauth.access_token.url,
            data=dict(
                code=authorization_code,
                secret=settings.oauth['secret'],
                applicationId=settings.oauth['application_id']
            )
        )
        if cas_access_token.status_code != 200:
            raise HTTPForbiden()

        result = json.loads(cas_access_token.text)
        return result['accessToken'], result['memberId']

    def get_member(self, member_id, access_token):

        response = requests.get(
            f'{settings.oauth.member.url}/{member_id}',
            headers={'authorization': f'oauth2-accesstoken {access_token}'}
        )
        if response.status_code != 200:
            raise HTTPForbidden()

        return json.loads(response.text)

