from bddrest import status, response, when

from dolphin.models import Member, Tag, Organization, OrganizationMember
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestTag(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='seconde Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123456788,
            reference_id=2,
        )
        session.add(cls.member2)

        cls.organization1 = Organization(
            title='first-organization',
        )
        session.add(cls.organization1)

        cls.organization2 = Organization(
            title='second-organization',
        )
        session.add(cls.organization2)
        session.flush()

        organization_member1 = OrganizationMember(
            organization_id=cls.organization1.id,
            member_id=cls.member1.id,
            role='owner',
        )
        session.add(organization_member1)

        organization_member2 = OrganizationMember(
            organization_id=cls.organization2.id,
            member_id=cls.member2.id,
            role='owner',
        )
        session.add(organization_member2)

        cls.tag = Tag(
            title='already exist',
            organization_id=cls.organization1.id,
        )
        session.add(cls.tag)
        session.commit()

    def test_get(self):
        self.login(
            email=self.member1.email,
            organization_id=self.organization1.id
        )

        with oauth_mockup_server(), self.given(
            f'Getting a tag',
            f'/apiv1/tags/id: {self.tag.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.tag.id

            when(
                'Intended tag with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended tag not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            self.login(
                email=self.member2.email,
                organization_id=self.organization2.id
            )
            when(
                'Getting a tag by a member from another organization',
                authorization=self._authentication_token
            )
            assert status == 403

            when('Request is not authorized', authorization=None)
            assert status == 401

