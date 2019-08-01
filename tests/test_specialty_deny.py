from bddrest import status, response, when, given

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Specialty, SpecialtyMember, Skill


class TestSpecialty(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member)
        skill = Skill(title='First Skill')

        cls.specialty = Specialty(
            title='First specialty',
            description='Sample description',
            members=[cls.member],
            skill=skill,
        )
        session.add(cls.specialty)
        session.commit()

    def test_deny(self):
        self.login(self.member.email)
        session = self.create_session()

        with oauth_mockup_server(), self.given(
            f'Denying a specialty',
            f'/apiv1/members/member_id: {self.member.id}/' \
            f'specialties/specialty_id: {self.specialty.id}',
            f'DENY',
            json=dict(
                memberId=self.member.id,
            )
        ):
            assert status == 200
            assert response.json['title'] == self.specialty.title
            assert response.json['description'] == self.specialty.description
            assert not session.query(SpecialtyMember) \
                .filter(
                    SpecialtyMember.specialty_id == self.specialty.id,
                    SpecialtyMember.member_id == self.member.id
                ) \
                .one_or_none()

            when('Specialty is not granted to member yet')
            assert status == '656 Specialty Not Granted Yet'

            when(
                'Intended specialty with string type not found',
                url_parameters=given | dict(specialty_id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended specialty with integer type not found',
                url_parameters=given | dict(specialty_id=0)
            )
            assert status == 404

            when(
                'Intended member with string type not found',
                url_parameters=given | dict(member_id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended member with integer type not found',
                url_parameters=given | dict(member_id=0)
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

