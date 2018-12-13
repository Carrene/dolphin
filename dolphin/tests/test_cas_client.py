from datetime import datetime, timedelta

from bddrest.authoring import status, when, Remove, Update

from dolphin.models import Member, Organization, OrganizationMember, Invitation
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, oauth_server_status


class TestToken(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.owner = Member(
            title='Owner',
            email='owner1@example.com',
            access_token='access token 1',
            phone=222222222,
            reference_id=1
        )
        session.add(cls.owner)

        cls.member= Member(
            title='Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=333333333,
            reference_id=2
        )
        session.add(cls.member)

        cls.organization = Organization(
            title='organization-title',
        )
        session.add(cls.organization)
        session.flush()

        cls.organization_member = OrganizationMember(
            organization_id=cls.organization.id,
            member_reference_id=cls.owner.reference_id,
            role='owner',
        )
        session.add(cls.organization_member)
        invitation = Invitation(
            email=cls.member.email,
            organization_id=cls.organization.id,
            by_member_id=cls.owner.id,
            role='member',
            expired_date=datetime.now() + timedelta(days=1),
            accepted=False
        )
        session.add(invitation)
        session.commit()

    def test_get_access_token(self):
        with oauth_mockup_server(), self.given(
                'Try to get an access token from CAS',
                '/apiv1/oauth2/tokens',
                'OBTAIN',
                form=dict(
                    authorizationCode='authorization code',
                    organizationId=self.organization.id
                )
            ):
                assert status == 200

                when(
                    '',
                    form=Update(authorizationCode='authorization code 2')
                )
                assert status == 200

                when(
                    'Trying to pass without the organization id  parameter',
                    form=Remove('organizationId')
                )
                assert status == '761 Organization Id Not In Form'

                when(
                    'Invalid the type of organization id',
                    form=Update(organizationId='not integer')
                )
                assert status == '763 Invalid Organization Id Type'


                when(
                    'Trying to pass without the authorization code parameter',
                    form=Remove('authorizationCode')
                )
                assert status == '762 Authorization Code Not In Form'

                when(
                    'Trying to pass with damage authorization code',
                    form=Update(authorizationCode='token is damage')
                )
                assert status == 403

                with oauth_server_status('404 Not Found'):
                    when('Chat server is not found')
                    assert status == '619 CAS Server Not Found'

                with oauth_server_status('503 Service Unavailable'):
                    when('Chat server is not available')
                    assert status == '802 CAS Server Not Available'

                with oauth_server_status(
                    '605 We Don\'t Recognize This Application'
                ):
                    when('Application ID in configuration is invalid')
                    assert status == '620 Invalid Application ID'

                with oauth_server_status('608 Malformed Secret'):
                    when('Application Secret is manipulated')
                    assert status == '621 Invalid Secret'

                with oauth_server_status('609 Token Expired'):
                    when('Token is expired')
                    assert status == 401

                with oauth_server_status('610 Malformed Access Token'):
                    when('Access token is manipulated')
                    assert status == 401

