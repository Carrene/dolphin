from bddrest.authoring import when, response, Remove, Update, status

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Member


class TestToken(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        member = Member(
            email='already.added@example.com',
            title='user',
            password='123456',
            phone=123456789
        )
        session.add(member)
        session.commit()

    def test_login(self):
        with self.given(
            'Login user',
            '/apiv1/tokens',
            'CREATE',
            form=dict(email='already.added@example.com', password='123456')
        ):
            assert response.status == 200
            when('Invalid email', form=Update(email='user@example.com'))
            assert response.status == 400
            when(
                'Invalid password',
                form=Update(
                    email='already.added@example.com',
                    password='1234567'
                )
            )
            assert response.status == 400
            when('Request without email parameters', form=Remove('email'))
            assert status == 400
            when(
                'Request without password parameters',
                form=Remove('password')
            )
            assert status == 400

