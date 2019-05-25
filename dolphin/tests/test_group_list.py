from bddrest import status, response, when, given

from dolphin.models import Member, Group
from dolphin.tests.helpers import LocalApplicationTestCase


class TestListGroup(LocalApplicationTestCase):

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

        group1 = Group(
            title='group1',
            members=[cls.member],
        )
        session.add(group1)

        group2 = Group(
            title='group2',
            members=[cls.member],
        )
        session.add(group2)

        group3 = Group(title='group3')
        session.add(group3)
        session.commit()

    def test_list_group(self):
        self.login(self.member.email, self.member.password)

        with self.given(
            'List group',
            '/apiv1/groups',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

    def test_list_groups_of_member(self):
        self.login('member1@example.com')

        with self.given(
            f'List groups of member\'s',
            f'/apiv1/members/id: {self.member.id}/groups',
            f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when(
                'Member not found',
                url_parameters=given | dict(id=0),
            )
            assert status == 404

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] < response.json[1]['id']

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] > response.json[1]['id']

            when('Trying pagination response', query=dict(take=1))
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Request is not authorized', authorization=None)
            assert status == 401

