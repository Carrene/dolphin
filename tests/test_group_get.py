from bddrest import status, response, when

from dolphin.models import Member, Group
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestGetGroup(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member)

        cls.group1 = Group(title='group1')
        session.add(cls.group1)

        session.commit()

    def test_get_group(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            f'Get group',
            f'/apiv1/groups/id: {self.group1.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.group1.id

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

