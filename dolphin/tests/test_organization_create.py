import io
from os.path import dirname, abspath, join

from nanohttp import settings
from bddrest.authoring import when, status, response, given

from dolphin.models import Member, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


TEST_DIR = abspath(dirname(__file__))
STUFF_DIR = join(TEST_DIR, 'stuff')
VALID_LOGO_PATH = join(STUFF_DIR, 'logo-225x225.jpg')
INVALID_FORMAT_LOGO_PATH = join(STUFF_DIR, 'test.pdf')
INVALID_MAXIMUM_SIZE_LOGO_PATH = join(STUFF_DIR, 'logo-550x550.jpg')
INVALID_MINIMUM_SIZE_LOGO_PATH = join(STUFF_DIR, 'logo-50x50.jpg')
INVALID_RATIO_LOGO_PATH = join(STUFF_DIR, 'logo-150x100.jpg')
INVALID_MAXMIMUM_LENGTH_LOGO_PATH = join(STUFF_DIR, 'maximum-length-30.jpg')


class TestOrganization(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
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
        settings.attachments.organizations.logos.max_length = 30

        with oauth_mockup_server(),  self.given(
            'The organization has successfully created',
            '/apiv1/organizations',
            'CREATE',
            multipart=dict(title=title)
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
                multipart=dict(title='organization-title')
            )
            assert status == '600 Repetitive Title'

            when(
                'The title format is invalid',
                multipart=dict(title='my organ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'The length of title is too long',
                multipart=dict(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'The title not in form',
                multipart=given - 'title' + dict(a='a')
            )
            assert status == '710 Title Not In Form'

            when('Trying to pass with empty form', multipart={})
            assert status == '400 Empty Form'

            with open(INVALID_MAXIMUM_SIZE_LOGO_PATH, 'rb') as f:
                when(
                    'The logo size is exceeded the maximum size',
                    multipart=dict(title='newtitle', logo=io.BytesIO(f.read()))
                )
                assert status == '625 Maximum allowed width is:  200, '\
                    'but the  550 is given.'

            with open(INVALID_MINIMUM_SIZE_LOGO_PATH, 'rb') as f:
                when(
                    'The logo size is less than minimum size',
                    multipart=dict(title='newtitle', logo=io.BytesIO(f.read()))
                )
                assert status == '625 Minimum allowed width is:  100, '\
                    'but the  50 is given.'

            with open(INVALID_RATIO_LOGO_PATH, 'rb') as f:
                when(
                    'Aspect ratio of the logo is invalid',
                    multipart=dict(title='newtitle', logo=io.BytesIO(f.read()))
                )
                assert status == '622 Invalid aspect ratio Only ' \
                    '1/1 is accepted.'

            with open(INVALID_FORMAT_LOGO_PATH, 'rb') as f:
                when(
                    'Format of the avatar is invalid',
                    multipart=dict(title='newtitle', logo=io.BytesIO(f.read()))
                )
                assert status == '623 Invalid content type, Valid options '\
                    'are: image/jpeg, image/png'

            with open(INVALID_MAXMIMUM_LENGTH_LOGO_PATH, 'rb') as f:
                when(
                    'The maxmimum length of avatar is invalid',
                    multipart=dict(title='newtitle', logo=io.BytesIO(f.read()))
                )
                assert status == '624 Cannot store files larger than: '\
                    '30720 bytes'

            when('Trying with an unauthorized member', authorization=None)
            assert status == 401

