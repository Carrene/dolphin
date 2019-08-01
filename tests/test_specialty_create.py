from bddrest import status, response, when, Remove, Update

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Specialty, Skill


class TestSpecialty(LocalApplicationTestCase):

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
            title='first skill',
        )
        cls.specialty = Specialty(
            title='Already-added',
            skill=cls.skill,
        )

        session.add(cls.skill)
        session.add(cls.specialty)
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        title = 'first specialty'

        with oauth_mockup_server(), self.given(
            'Creating a specialty',
            '/apiv1/specialties',
            'CREATE',
            json=dict(
                title=title,
                description='A description for specialty',
                skillId=self.skill.id
            ),
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['id'] is not None
            assert response.json['description'] is not None
            assert response.json['skillId'] is not None

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with invalid form parameters',
                json=dict(a='a'),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, skillId'

            when(
                'Trying to pass with repetitive title',
                json=dict(title=self.specialty.title),
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

