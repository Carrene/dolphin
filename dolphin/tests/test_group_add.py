from bddrest import status, response, when

from dolphin.models import Member, Group, GroupMember
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestGroup(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            phone=123456788,
        )
        session.add(cls.member2)

        cls.group = Group(
            title='first group',
        )
        session.add(cls.group)
        session.flush()

        group_member = GroupMember(
            group_id=cls.group.id,
            member_id=cls.member2.id
        )
        session.add(group_member)
        session.commit()

    def test_add(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            f'Adding a member to a group',
            f'/apiv1/groups/id: {self.group.id}',
            f'ADD',
            json=dict(memberId=self.member1.id),
        ):
            assert status == 200
            assert response.json['id'] == self.group.id

            session = self.create_session()
            assert session.query(GroupMember) \
                .filter(
                    GroupMember.group_id == self.group.id,
                    GroupMember.member_id == self.member1.id
                ) \
                .one_or_none()

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when('Group not found', url_parameters=dict(id=0))
            assert status == 404

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Member is not found',
                json=dict(memberId=0),
            )
            assert status == '610 Member Not Found'

            when(
                'Trying to pass with invalid member id type',
                json=dict(memberId='not-integer'),
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'Trying to pass without member id',
                json=dict(a='a'),
            )
            assert status == '735 Member Id Not In Form'

            when(
                'Trying to pass with none member id',
                json=dict(memberId=None)
            )
            assert status == '774 Member Id Is Null'

            when(
                'The member already added to group',
                json=dict(memberId=self.member2.id)
            )
            assert status == '652 Already Added To Group'

            when('Request is not authorized', authorization=None)
            assert status == 401

