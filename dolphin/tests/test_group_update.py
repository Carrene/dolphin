from bddrest import status, response, when, given

from dolphin.models import Member
from dolphin.tests.helpers import create_group, LocalApplicationTestCase, \
    oauth_mockup_server


class TestGroup(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
        )
        session.add(cls.member)

        cls.group1 = create_group(
            title='Already exists',
        )
        session.add(cls.group1)

        cls.group2 = create_group(
            title='group 1',
        )
        session.add(cls.group2)
        session.commit()

    def test_update(self):
        self.login(self.member.email)
        new_title = 'New title'
        new_description = 'A description for group'
        new_public = False

        with oauth_mockup_server(), self.given(
            f'Updating a group',
            f'/apiv1/groups/id: {self.group2.id}',
            f'UPDATE',
            json=dict(
                title=new_title,
                description=new_description,
                public=new_public,
            ),
        ):
            assert status == 200
            assert response.json['id'] == self.group2.id
            assert response.json['title'] == new_title
            assert response.json['description'] == new_description
            assert response.json['public'] == new_public

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group with integer type not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when('Trying to pass with same title')
            assert status == 200

            when(
                'Title is repetitive',
                json=given | dict(title=self.group1.title)
            )
            assert status == '600 Repetitive Title'

            when(
                'Title length is more than limit',
                json=given | dict(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when('Invalid parameter is in the form', json=dict(a='a'))
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, public'

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when('Request is not authorized', authorization=None)
            assert status == 401

