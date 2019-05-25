from bddrest.authoring import response, status, when, Update

from dolphin.models import Member
from dolphin.tests.helpers import LocalApplicationTestCase


class TestLogin(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        member = Member(
            email='member@example.com',
            title='First Member',
            password='123abcABC',
            role='member'
        )
        session = cls.create_session()
        session.add(member)
        session.commit()

    def test_create_token(self):
        email = 'member@example.com'
        password = '123abcABC'

        with self.given(
            'Create a login token',
            '/apiv1/tokens',
            'CREATE',
            form=dict(email=email, password=password)
        ):
            assert status == 200
            assert 'token' in response.json

            when('Invalid password', form=Update(password='123aA'))
            assert status == '663 Incorrect Email Or Password'

            when('Not exist email', form=Update(email='user@example.com'))
            assert status == '663 Incorrect Email Or Password'

            when('Invalid email format', form=Update(email='user.com'))
            assert status == '754 Invalid Email Format'

            when('Trying to pass with empty form', form={})
            assert status == '400 Empty Form'

