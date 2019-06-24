import io
import os
from os.path import abspath, dirname, join

from ..oauth.tokens import AccessToken
from bddrest import status, response, when
from nanohttp import settings
from sqlalchemy_media import StoreManager

from dolphin.models import Member, Application
from dolphin.oauth.tokens import AccessToken
from dolphin.tests.helpers import LocalApplicationTestCase


TEST_DIR = abspath(dirname(__file__))
AVATAR_PATH = join(TEST_DIR, 'stuff/avatar-225x225.jpg')


class TestProject(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        with open(AVATAR_PATH, 'rb') as f:
            avatar = io.BytesIO(f.read())

        session = cls.create_session()
        with StoreManager(session):
            admin = Member(
                email='admin@example.com',
                title='admin_title',
                name='admin_name',
                access_token='access token 1',
                password='123abcABC',
                avatar=avatar,
                role='admin'
            )
            session.add(admin)

            owner = Member(
                email='owner@example.com',
                title='owner_title',
                name='owner_name',
                access_token='access token 2',
                password='123abcABC',
                avatar=avatar,
                role='member'
            )

            cls.member = Member(
                title='First Member',
                email='member1@example.com',
                password='123abcABC',
                role='member',
                name='member_name',
                access_token='access token 3',
                phone='+9891234567',
                avatar=avatar,
            )
            session.add(cls.member)

            cls.application1= Application(
                title='oauth',
                redirect_url='http://example1.com/oauth2',
                secret=os.urandom(32),
                owner=owner,
            )
            session.add(cls.application1)

            cls.application2 = Application(
                title='oauth',
                redirect_url='http://example2.com/oauth2',
                secret=os.urandom(32),
                owner=owner,
            )
            session.add(cls.application2)
            session.commit()

    def test_get_member_by_me(self):
        self.login(
            email='member1@example.com',
            password='123abcABC',
            organization_id=1,
        )

        with self.given(
            'Get member according to scopes',
            f'/apiv1/members/id: me',
            'GET',
        ):
            assert status == 200
            assert response.json['title'] == self.member.title
            assert response.json['id'] == self.member.id
            assert response.json['email'] is None
            assert response.json['name'] is None
            assert response.json['avatar'] is None
            assert response.json['phone'] is None
#
#            when('Trying to pass without authorization headers', headers={})
#            assert status == 401
#
#            when(
#                'Trying to pass with damege token',
#                headers={'authorization': 'oauth2-accesstoken token'}
#            )
#            assert status == '610 Malformed Access Token'
#
#            access_token_payload['scopes'] = [
#                'name',
#                'email',
#                'avatar',
#                'phone',
#            ]
#            access_token = AccessToken(access_token_payload).dump().decode()
#            when(
#                'Trying to pass with multi scope',
#                headers={'authorization': f'oauth2-accesstoken {access_token}'}
#            )
#            assert response.json['name'] == self.member.name
#            assert response.json['email'] == self.member.email
#            assert response.json['avatar'] is not None
#            assert response.json['phone'] == self.member.phone
#            assert response.json['id'] == self.member.id
#
#            settings.access_token.max_age = 0.1
#            access_token = AccessToken(access_token_payload).dump().decode()
#            time.sleep(1)
#            when(
#                'Trying to pass with expired token',
#                headers={'authorization': f'oauth2-accesstoken {access_token}'}
#            )
#            assert status == '609 Token Expired'
#
#            access_token_payload = dict(
#                applicationId=self.application1.id,
#                memberId=self.member.id,
#            )
#            access_token = AccessToken(access_token_payload).dump().decode()
#            when(
#                'Trying to pass with empty scopes in the access token',
#                headers={'authorization': f'oauth2-accesstoken {access_token}'}
#            )
#            assert response.json['id'] == self.member.id
#            assert response.json['name'] is None
#            assert response.json['email'] is None
#            assert response.json['avatar'] is None
#            assert response.json['phone'] is None
#
#            access_token_payload = dict(
#                applicationId=self.application2.id,
#                memberId=self.member.id,
#                scopes=['title']
#            )
#            access_token = AccessToken(access_token_payload).dump().decode()
#            when(
#                'The member revoke the authorization application',
#                headers={'authorization': f'oauth2-accesstoken {access_token}'}
#            )
#            assert status == 403
#
#        self.login(email=self.member.email, password='123abcABC')
#        with self.given(
#            'Get member as member',
#            '/apiv1/members/id:me',
#            'GET',
#        ):
#            assert status == 200
#            assert response.json['id'] == self.member.id
#
#            when('Trying to get another member', url_parameters=dict(id=1))
#            assert status == 403
#
#    def test_get_member_by_id(self):
#        self.login(email='member1@example.com', password='123abcABC')
#
#        with oauth_mockup_server(), self.given(
#            'Getting a project',
#            f'/apiv1/members/id:{self.member.id}',
#            'GET'
#        ):
#            assert status == 200
#            assert response.json['id'] == self.member.id
#            assert response.json['title'] == 'member1'
#
#            when(
#                'Intended project with string type not found',
#                url_parameters=dict(id='Alphabetical')
#            )
#            assert status == 404
#
#            when(
#                'Intended project with string type not found',
#                url_parameters=dict(id=100)
#            )
#            assert status == 404
#
#            when(
#                'Form parameter is sent with request',
#                form=dict(parameter='Invalid form parameter')
#            )
#            assert status == '709 Form Not Allowed'
#
#            when('Request is not authorized', authorization=None)
#            assert status == 401
#
