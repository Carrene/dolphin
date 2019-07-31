from bddrest.authoring import when, status, response

from dolphin.models import Member, Organization, OrganizationMember, Group, \
    Specialty, Skill
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestOrganizationMembers(LocalApplicationTestCase):

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

        cls.organization1 = Organization(
            title='organization-title-1',
        )
        session.add(cls.organization1)
        session.flush()

        organization_member1 = OrganizationMember(
            member_id=cls.owner.id,
            organization_id=cls.organization1.id,
            role='owner',
        )
        session.add(organization_member1)

        organization_member2 = OrganizationMember(
            member_id=cls.member.id,
            organization_id=cls.organization1.id,
            role='member',
        )
        session.add(organization_member2)
        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
            members=[cls.member],
        )

        session.add(specialty)

        group = Group(
            title='group1',
            members=[cls.member],
        )
        session.add(group)
        session.commit()

    def test_list(self):
        self.login(
            email=self.owner.email,
            organization_id=self.organization1.id
        )

        with oauth_mockup_server(), self.given(
            f'List of organizationi',
            f'/apiv1/organizations/id: {self.organization1.id}/members',
            f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            owner = response.json[0] \
                if response.json[0]['id'] == self.owner.id \
                else response.json[1]

            member = response.json[0] \
                if response.json[0]['id'] == self.member.id \
                else response.json[1]

            assert member['organizationRole'] == 'member'
            assert owner['organizationRole'] == 'owner'

            assert member['specialties'] is not None
            assert member['groups'] is not None

            when('Trying to pass with wrong id', url_parameters=dict(id=0))
            assert status == 404

            when(
                'Type of id is invalid',
                url_parameters=dict(id='not-integer')
            )
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
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
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

