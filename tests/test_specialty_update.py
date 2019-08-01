from bddrest import status, response, when, Update

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

        skill = Skill(title='First Skill')
        cls.specialty1 = Specialty(
            title='Already-added',
            description='A description for specialty',
            skill=skill,
        )
        session.add(cls.specialty1)

        cls.specialty2 = Specialty(
            title='Second specialty',
            description='A description for second specialty',
            skill=skill,
        )
        session.add(cls.specialty2)
        session.commit()

    def test_update(self):
        self.login(self.member.email)
        title = 'first specialty'

        with oauth_mockup_server(), self.given(
            'Creating a specialty',
            f'/apiv1/specialties/id: {self.specialty1.id}',
            'UPDATE',
            json=dict(
                title=title,
                description='Another description',
            ),
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['id'] is not None
            assert response.json['description'] is not None

            when('Specialty not found', url_parameters=dict(id=0))
            assert status == 404

            when(
                'Intended specialty with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Trying to send title which intended specialty already has',
                json=dict(title=title),
            )
            assert status == 200

            when(
                'Title is same as title of another specialty',
                json=dict(title=self.specialty2.title),
            )
            assert status == '600 Repetitive Title'

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with invalid form parameters',
                json=dict(a='a'),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, skillId'

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
                'Description length is more than limit',
                json=Update(description=((512 + 1) * 'a'))
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when('Request is not authorized', authorization=None)
            assert status == 401

