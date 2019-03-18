from bddrest import status, response, when, Remove, Update

from dolphin.models import Member, Skill
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestSkill(LocalApplicationTestCase):

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

        cls.skill = Skill(
            title='Already-added',
        )
        session.add(cls.skill)
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        title = 'first skill'

        with oauth_mockup_server(), self.given(
            'Creating a skill',
            '/apiv1/skills',
            'CREATE',
            json=dict(
                title=title,
                description='A description for skill',
            ),
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['id'] is not None
            assert response.json['description'] is not None

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with invalid form parameters',
                json=dict(a='a'),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description'

            when(
                'Trying to pass with repetitive title',
                json=dict(title=self.skill.title),
            )
            assert status == '600 Repetitive Title'

            when(
                'Title length is more than limit',
                json=dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Trying to pass with null title',
                json=dict(title=None)
            )
            assert status == '727 Title Is Null'

            when(
                'Trying to pass without title',
                json=Remove('title')
            )
            assert status == '710 Title Not In Form'

            when(
                'Description length is more than limit',
                json=Update(description=((512 + 1) * 'a'))
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when('Request is not authorized', authorization=None)
            assert status == 401

