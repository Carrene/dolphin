from bddrest.authoring import when, status, response

from dolphin.models import Member, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestOrganization(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.owner = Member(
            title='Owner',
            email='owner1@example.com',
            access_token='access token 1',
            phone=222222222,
            reference_id=2
        )
        session.add(cls.owner)

        cls.member= Member(
            title='Member',
            email='member1@example.com',
            access_token='access token 2',
            phone=333333333,
            reference_id=3
        )
        session.add(cls.member)

        cls.organization = Organization(
            title='organization-title',
        )
        session.add(cls.organization)
        session.flush()

        cls.organization_member = OrganizationMember(
            organization_id=cls.organization.id,
            member_id=cls.owner.id,
            role='owner',
        )
        session.add(cls.organization_member)
        session.commit()

    def test_get(self):
        self.login(email=self.owner.email)

        with oauth_mockup_server(), self.given(
            f'Get one of my organization using id',
            f'/apiv1/organizations/id: {self.organization.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.organization.id
            assert response.json['title'] == self.organization.title
            assert response.json['role'] == self.organization_member.role
            assert response.json['membersCount'] == 1

            when('Trying to pass with wrong id', url_parameters=dict(id=0))
            assert status == 404

            when('Type of id is invalid', url_parameters=dict(id='not-integer'))
            assert status == 404

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying with an unauthorized member', authorization=None)
            assert status == 401

            self.logout()
            self.login(email=self.member.email)
            when(
                'The user not member of organization',
                authorization=self._authentication_token
            )
            assert status == 404

