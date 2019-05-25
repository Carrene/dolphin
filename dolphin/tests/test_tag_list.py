from bddrest import when, response, status

from dolphin.models import Tag, Member, Organization, OrganizationMember
from dolphin.tests.helpers import  LocalApplicationTestCase


class TestTag(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)

        cls.organization = Organization(
            title='organization-title',
        )
        session.add(cls.organization)
        session.flush()

        organization_member = OrganizationMember(
            organization_id=cls.organization.id,
            member_id=cls.member.id,
            role='owner',
        )
        session.add(organization_member)

        tag1 = Tag(
            title='first tag',
            organization_id=cls.organization.id,
        )
        session.add(tag1)

        tag2 = Tag(
            title='second tag',
            organization_id=cls.organization.id,
        )
        session.add(tag2)
        session.commit()


    def test_list(self):
        principal = self.member.create_jwt_principal()
        principal.payload['organizationId'] = self.organization.id
        self._authentication_token = principal.dump().decode('utf-8')

        with self.given(
            'List of tags',
            '/apiv1/tags',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

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
            when('Request is not authorized', authorization=None)
            assert status == 401

