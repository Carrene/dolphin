from bddrest import status, response, when, Update

from dolphin.models import Member, Group
from dolphin.tests.helpers import create_group, LocalApplicationTestCase, \
    oauth_mockup_server


class TestGroup(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member)

        cls.group = create_group()
        session.add(cls.group)
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        title = 'first group'
        description = 'A description for a group'

        with oauth_mockup_server(), self.given(
            'Creating a group',
            '/apiv1/groups',
            'CREATE',
            json=dict(
                title=title,
                description=description,
            ),
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['description'] == description
            assert response.json['id'] is not None

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with repetitive title',
                json=dict(title=self.group.title),
            )
            assert status == '600 Repetitive Title'

            when(
                'Trying to pass without title',
                json=dict(a='a'),
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                json=dict(title=((128 + 1) * 'a'))
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'Trying to pass with none title',
                json=dict(title=None)
            )
            assert status == '727 Title Is Null'

            when(
                'Description length is less than limit',
                json=Update(description=((8192 + 1) * 'a')),
            )
            assert status == '703 At Most 8192 Characters Are Valid For ' \
                'Description'

            when('Request is not authorized', authorization=None)
            assert status == 401

