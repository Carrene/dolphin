from bddrest.authoring import when, status, response, given

from dolphin.models import Member, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase


class TestApplication(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        member = Member(
            email='already.added@example.com',
            title='username',
            password='123abcABC',
            role='member'
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

    def test_create_organization(self):
        title = 'My-organization'
        self.login(email='already.added@example.com', password='123abcABC')

        with self.given(
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
            assert status == '622 Organization Title Is Already Taken'

            when('The title format is invalid', form=dict(title='my organ'))
            assert status == 705

            when(
                'The length of title is too long',
                form=dict(title=(40 + 1) * 'a')
            )
            assert status == 720

            when('The title not in form', form=given - 'title' + dict(a='a'))
            assert status == 718

            when('Trying to pass with empty form', form={})
            assert status == '400 Empty Form'

            when('Trying with an unauthorized member', authorization=None)
            assert status == 401

