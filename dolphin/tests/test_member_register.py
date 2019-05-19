import time

from bddrest.authoring import response, Update, when, status, Remove
from nanohttp import settings

from dolphin.models import Member
from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.tokens import RegistrationToken


class TestRegisteration(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        member = Member(
            email='already.added@example.com',
            title='username',
            password='123abcABC',
            role='member',
            reference_id=1,
        )
        session = cls.create_session()
        session.add(member)
        session.commit()

    def test_register_member(self):
        email = 'user@example.com'
        title = 'nickname'
        password = '123abdABD'
        registration_token = RegistrationToken(dict(email=email)).dump()

        with self.given(
            'Register a member',
            '/apiv1/members',
            'REGISTER',
            form=dict(
                title=title,
                password=password,
                ownershipToken=registration_token
            )
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['email'] == email
            assert 'id' in response.json
            assert 'X-New-JWT-Token' in response.headers

            when('Invalid password min length', form=Update(password='1Aa'))
            assert status == '702 Invalid Password Length'

            when(
                'Invalid password max length',
                form=Update(password='1Aa123456789abcdeABCD')
            )
            assert status == '702 Invalid Password Length'

            when(
                'Invalid title format',
                form=Update(password='123AAAaaa', title='1username')
            )
            assert status == '705 Invalid Title Format'

            when('Duplicate title', form=Update(title='username'))
            assert status == '604 Title Is Already Registered'

            when('Duplicate Email', form=Update(title='user_name'))
            assert status == '601 Email Address Is Already Registered'

            when('The token has been damaged',
                form=Update(ownershipToken='token')
            )
            assert status == '611 Malformed Token'

            settings.registration.max_age = 0.3
            registration_token = RegistrationToken(dict(email=email)).dump()
            time.sleep(1)
            when(
                'The token is expired',
                form=Update(ownershipToken=registration_token)
            )
            assert status == '609 Token Expired'

            when('Trying to pass with empty form', form={})
            assert status == '400 Empty Form'

            when(
                'Trying to pass without ownership token',
                form=Remove('ownershipToken')
            )
            assert status == '727 Token Not In Form'

            when('Trying to pass without title', form=Remove('title'))
            assert status == '718 Title Not In Form'

            when('Trying to pass without password', form=Remove('password'))
            assert status == '728 Password Not In Form'

