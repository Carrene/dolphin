from bddrest import status, response, when

from dolphin.models import Member, Specialty, Skill
from .helpers import LocalApplicationTestCase, oauth_mockup_server


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
        cls.specialty = Specialty(
            title='specialty 1',
            description='A description',
            skill=skill,
        )
        session.add(cls.specialty)
        session.commit()

    def test_get(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Getting a specialty',
            f'/apiv1/specialties/id: {self.specialty.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.specialty.id

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

