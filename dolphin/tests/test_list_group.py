from bddrest import status, response

from dolphin.models import Member, Group
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestListGroup(LocalApplicationTestCase):

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

        group1 = Group(title='group1')
        session.add(group1)

        group2 = Group(title='group2')
        session.add(group2)

        group3 = Group(title='group3')
        session.add(group3)

        session.commit()

    def test_list_group(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List group',
            '/apiv1/groups',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3
