from bddrest.authoring import when, status, response, given

from dolphin.models import Member, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestOrganization(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member)

        organization = Organization(
            title='organization-title',
        )
        session.add(organization)
        session.flush()

        organization_member = OrganizationMember(
            organization_id=organization.id,
            member_id=member.id,
            role='owner',
        )
        session.add(organization_member)
        session.commit()

    def test_create(self):
        title = 'My-organization'
        self.login(email='member1@example.com')

        with oauth_mockup_server(),  self.given(
            'The organization has successfully created',
            '/apiv1/organizations',
            'CREATE',
            form=dict(title=title)
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['logo'] is None
            assert response.json['url'] is None
            assert response.json['domain'] is None
            assert response.json['createdAt'] is not None
            assert response.json['modifiedAt'] is None

            when(
                'The organization title is exist',
                form=dict(title='organization-title')
            )
            assert status == '600 Repetitive Title'

            when('The title format is invalid', form=dict(title='my organ'))
            assert status == '747 Invalid Title Format'

            when(
                'The length of title is too long',
                form=dict(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when('The title not in form', form=given - 'title' + dict(a='a'))
            assert status == '710 Title Not In Form'

            when('Trying to pass with empty form', form={})
            assert status == '400 Empty Form'

            when('Trying with an unauthorized member', authorization=None)
            assert status == 401

