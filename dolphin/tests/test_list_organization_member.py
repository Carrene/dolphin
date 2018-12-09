from bddrest.authoring import when, status, response
 from panda.models import Member, Organization, OrganizationMember
from panda.tests.helpers import LocalApplicationTestCase


 class TestOrganizationMembers(LocalApplicationTestCase):

     @classmethod
    def mockup(cls):
        session = cls.create_session()
        owner1 = Member(
            email='owner1@example.com',
            title='owner1',
            password='123456',
            role='member'
        )
        session.add(owner1)
         member1 = Member(
            email='member1@example.com',
            title='member1',
            password='123456',
            role='member'
        )
        session.add(member1)
         cls.organization1 = Organization(
            title='organization-title-1',
        )
        session.add(cls.organization1)
        session.flush()
         organization_member1 = OrganizationMember(
            member_id=owner1.id,
            organization_id=cls.organization1.id,
            role='owner',
        )
        session.add(organization_member1)
         organization_member2 = OrganizationMember(
            member_id=member1.id,
            organization_id=cls.organization1.id,
            role='member',
        )
        session.add(organization_member2)
        session.commit()

     def test_list(self):
        self.login(email='owner1@example.com', password='123456')

         with self.given(
            f'List of organization',
            f'/apiv1/organizations/id: {self.organization1.id}/'
                'organizationmembers',
            f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('Trying to pass with wrong id', url_parameters=dict(id=0))
            assert status == 404

            when('Type of id is invalid', url_parameters=dict(id='id'))
            assert status == 404

            when('The request with form parameter', form=dict(param='param'))
            assert status == '400 Form Not Allowed'

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

            self.logout()
            when(
                'Trying with an unauthorized member',
                authorization=self._authentication_token
            )
            assert status == 401

