from bddrest.authoring import when, status, response

from dolphin.models import Member, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestOrganization(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.owner1 = Member(
            email='owner1@example.com',
            title='owner1',
            access_token='access token 1',
            phone=222222222,
            reference_id=2
        )
        session.add(cls.owner1)

        cls.member1 = Member(
            email='member1@example.com',
            title='member1',
            access_token='access token 3',
            phone=444444444,
            reference_id=4
        )
        session.add(cls.member1)

        organization1 = Organization(
            title='organization-title-1',
        )
        session.add(organization1)
        session.flush()

        organization_member1 = OrganizationMember(
            member_id = cls.owner1.id,
            organization_id = organization1.id,
            role = 'owner',
        )
        session.add(organization_member1)

        organization_member3 = OrganizationMember(
            member_id = cls.member1.id,
            organization_id = organization1.id,
            role = 'member',
        )
        session.add(organization_member3)

        organization2 = Organization(
            title='organization-title-2',
        )
        session.add(organization2)
        session.flush()

        organization_member4 = OrganizationMember(
            member_id = cls.owner1.id,
            organization_id = organization2.id,
            role = 'owner',
        )
        session.add(organization_member4)

        session.commit()

    def test_unauthorize_list(self):
        with self.given(
            'List of organization',
            '/apiv1/organizations',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when(
                'The request with email parameter',
                form=dict(email=self.owner1.email)
            )
            assert len(response.json) == 2

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] == 1
            assert response.json[1]['id'] == 2

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 2
            assert response.json[1]['id'] == 1

            when('Trying pagination response', query=dict(take=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert response.json[0]['id'] == 2
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

    def test_authoriz_list(self):
        self.login(email=self.owner1.email)

        with oauth_mockup_server(), self.given(
            f'List of organization',
            f'/apiv1/members/id: {self.owner1.id}/organizations',
            f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when(
                'Trying to pass with wrong member id',
                url_parameters=dict(id=self.member1.id)
            )
            assert status == 404

            when('Trying to pass with wrong id', url_parameters=dict(id=0))
            assert status == 404

            when('Type of id is invalid', url_parameters=dict(id='not-integer'))
            assert status == 404

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] == 1
            assert response.json[1]['id'] == 2

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 2
            assert response.json[1]['id'] == 1

            when('Trying pagination response', query=dict(take=1))
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            self.logout()
            when('Request is not authorized', authorization=None)
            assert status == 401

