import time

from bddrest.authoring import when, status, response, Update, given
from cas import CASPrincipal
from nanohttp import settings, context
from nanohttp.contexts import Context

from dolphin.models import Member, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.tokens import OrganizationInvitationToken


class TestOrganization(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session(expire_on_commit=True)
        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123456788,
            reference_id=3
        )
        session.add(cls.member2)

        cls.organization = Organization(
            title='organization-title',
        )
        session.add(cls.organization)
        session.flush()

        organization_member = OrganizationMember(
            organization_id=cls.organization.id,
            member_reference_id=cls.member1.reference_id,
            role='owner'
        )
        session.add(organization_member)
        session.commit()

    def test_join(self):
        self.login(email=self.member2.email)
        identity = CASPrincipal.load(self._authentication_token)
        with Context(dict()):
            context.identity = identity
            payload = dict(
                email=self.member2.email,
                organizationId=self.organization.id,
                memberReferenceId=self.member2.reference_id,
                ownerReferenceId=self.member1.reference_id,
                role='member',
            )
        token = OrganizationInvitationToken(payload)

        with oauth_mockup_server(), self.given(
            'Joining to the organization has successfully',
            '/apiv1/organizations',
            'JOIN',
            form=dict(token=token.dump())
        ):
            assert status == 200
            assert response.json['title'] == self.organization.title

            when('Trying again for join to the organization')
            assert status == '628 Already In This Organization'

            payload['organizationId'] = 100
            token = OrganizationInvitationToken(payload)
            when(
                'The organization not exist',
                form=Update(token=token.dump())
            )
            assert status == 404

            when(
                'Trying to pass without invitation token in form',
                form=given - 'token' | dict(a='a')
            )
            assert status == '757 Token Not In Form'

            when(
                'Trying to pass with malformed token',
                form=Update(token='Malformed token')
            )
            assert status == '626 Malformed Token'

            settings.organization_invitation.max_age = 0.3
            token = OrganizationInvitationToken(payload)
            invitation_token = token.dump()
            time.sleep(1)
            when(
                'Trying to pass with expired token',
                form=Update(token=invitation_token)
            )
            assert status == '627 Token Expired'

            when('Trying to pass without form parameters', form={})
            assert status == 400

            when('Trying with an unauthorized member', authorization=None)
            assert status == 401

