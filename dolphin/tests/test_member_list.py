from bddrest import status, response, when

from dolphin.models import Member
from dolphin.tests.helpers import LocalApplicationTestCase


class TestMember(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            phone=123987465,
            password='123ABCabc',
        )
        session.add(cls.member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            phone=1287465,
            password='123ABCabc',
        )
        session.add(member2)

        cls.member3 = Member(
            title='Third Member',
            email='member3@example.com',
            phone=1287456,
            password='123ABCabc',
        )
        session.add(cls.member3)
        session.commit()

    def test_list(self):
        self.login(self.member1.email)

        with self.given(
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
            assert response.json[0]['title'] == self.member1.title

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == self.member3.title

            when(
                'List members except one of them',
                query=dict(title='!Second Member')
            )
            assert len(response.json) == 2

            when(
                'Member pagination',
                query=dict(sort='id', take=1, skip=2)
            )
            assert response.json[0]['title'] == self.member3.title

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == self.member1.title

            when('Request is not authorized', authorization=None)
            assert status == 401

