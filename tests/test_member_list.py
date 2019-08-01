from bddrest import status, response, when

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member


class TestMember(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123987465,
            reference_id=3
        )
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token',
            phone=1287465,
            reference_id=4
        )
        session.add(member2)

        member3 = Member(
            title='Third Member',
            email='member3@example.com',
            access_token='access token',
            phone=1287456,
            reference_id=5
        )
        session.add(member3)
        session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List members',
            '/apiv1/members',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when(
                'Sort members by title',
                query=dict(sort='title')
            )
            assert status == 200
            assert response.json[0]['title'] == 'member1'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'Third Member'

            when(
                'List members except one of them',
                query=dict(title='!Second Member')
            )
            assert len(response.json) == 2

            when(
                'Member pagination',
                query=dict(sort='id', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'Third Member'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'member1'

            when('Request is not authorized', authorization=None)
            assert status == 401

