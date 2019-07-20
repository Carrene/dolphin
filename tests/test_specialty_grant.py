from bddrest import status, response, when, given

from dolphin.models import Member, Specialty, SpecialtyMember
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
            reference_id=2
        )
        session.add(cls.member)

        cls.specialty = Specialty(
            title='First specialty',
            description='Sample description',
        )
        session.add(cls.specialty)
        session.commit()

    def test_grant(self):
        self.login(self.member.email)
        session = self.create_session()

        with oauth_mockup_server(), self.given(
            f'Granting a specialty',
            f'/apiv1/members/member_id: {self.member.id}/' \
            f'specialties/specialty_id: {self.specialty.id}',
            f'GRANT',
        ):
            assert status == 200
            assert response.json['title'] == self.specialty.title
            assert response.json['description'] == self.specialty.description
            assert session.query(SpecialtyMember) \
                .filter(
                    SpecialtyMember.specialty_id == self.specialty.id,
                    SpecialtyMember.member_id == self.member.id
                ) \
                .one()

            when('Specialty is already granted to member')
            assert status == '655 Specialty Already Granted'

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

