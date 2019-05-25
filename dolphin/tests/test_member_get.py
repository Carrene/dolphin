from bddrest import status, response, when

from dolphin.models import Member
from dolphin.tests.helpers import LocalApplicationTestCase


class TestMember(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)
        session.commit()

    def test_get(self):
        self.login(self.member.email)

        with self.given(
            'Getting a member',
            f'/apiv1/members/id: {self.member.id}',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == self.member.id
            assert response.json['title'] == self.member.title

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

