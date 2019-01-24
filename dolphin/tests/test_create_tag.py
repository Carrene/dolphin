from bddrest import status, response, when

from dolphin.models import Member, Tag, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestTag(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
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

        cls.tag = Tag(
            title='already exist',
            organization_id=cls.organization.id,
        )
        session.add(cls.tag)
        session.commit()

    def test_create(self):
        self.login(
            email=self.member.email,
            organization_id=self.organization.id
        )
        title = 'first tag'

        with oauth_mockup_server(), self.given(
            'Creating a tag',
            '/apiv1/tags',
            'CREATE',
            json=dict(title=title),
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['id'] is not None

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with repetitive title',
                json=dict(title=self.tag.title),
            )
            assert status == '600 Repetitive Title'

            when(
                'Trying to pass without title',
                json=dict(a='a'),
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                json=dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Trying to pass with none title',
                json=dict(title=None)
            )
            assert status == '727 Title Is None'

            when('Request is not authorized', authorization=None)
            assert status == 401

