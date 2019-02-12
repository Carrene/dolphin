from bddrest.authoring import when, status, response, Update, Remove
from restfulpy.messaging import create_messenger

from dolphin.models import Member, Organization, OrganizationMember, \
   OrganizationInvitationEmail
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.tokens import OrganizationInvitationToken


class TestOrganization(LocalApplicationTestCase):
    __configuration__ = '''
      messaging:
        default_messenger: restfulpy.mockup.MockupMessenger
    '''

    @classmethod
    def mockup(cls):
        session = cls.create_session()
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

        cls.member3 = Member(
            title='Third Member',
            email='member3@example.com',
            access_token='access token 3',
            phone=123456787,
            reference_id=4
        )
        session.add(cls.member3)

        cls.organization = Organization(
            title='organization-title',
        )
        session.add(cls.organization)
        session.flush()

        organization_member1 = OrganizationMember(
            organization_id=cls.organization.id,
            member_id=cls.member1.id,
            role='owner'
        )
        session.add(organization_member1)

        organization_member2 = OrganizationMember(
            organization_id=cls.organization.id,
            member_id=cls.member2.id,
            role='member'
        )
        session.add(organization_member2)
        session.commit()

    def test_invite(self):
        messenger = create_messenger()
        self.login(email=self.member1.email)

        with oauth_mockup_server(), self.given(
            f'Inviting to the organization has successfully created',
            f'/apiv1/organizations/id: {self.organization.id}/invitations',
            f'CREATE',
            form=dict(
                email=self.member3.email,
                role='member',
                scopes='title,email',
                applicationId=1,
                redirectUri='www.example.com',
            )
        ):

            assert status == 200
            assert response.json['email'] == self.member3.email
            assert response.json['id'] is not None

            task = OrganizationInvitationEmail.pop()
            task.do_(None)
            assert messenger.last_message['to'] == self.member3.email
            token = OrganizationInvitationToken.load(
                messenger.last_message['body']['token']
            )
            assert token.role == 'member'
            assert token.email == self.member3.email
            assert token.by_member_reference_id == self.member1.reference_id
            assert token.organization_id == self.organization.id

            when(
                'The organization not exist with this id',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Trying to pass using id is alphabetical',
                url_parameters=dict(id='not-integer')
            )
            assert status == 404

            when(
                'Trying to pass with not exist user',
                form=Update(email='not_exist_user@example.com')
            )
            assert status == 200

            when(
                'The email format is invalid',
                form=Update(email='example')
            )
            assert status == '754 Invalid Email Format'

            when(
                'Trying to pass without email parameter in form',
                form=Remove('email')
            )
            assert status == '753 Email Not In Form'

            when(
                'The role format is invalid',
                form=Update(role='example')
            )
            assert status == '756 Invalid Role Value'

            when(
                'Trying to pass without role parameter in form',
                form=Remove('role')
            )
            assert status == '755 Role Not In Form'

            when(
                'Trying to pass without scopes parameter in form',
                form=Remove('scopes')
            )
            assert status == '765 Scopes Not In Form'

            when(
                'Trying to pass without application id parameter in form',
                form=Remove('applicationId')
            )
            assert status == '764 Application Id Not In form'

            when(
                'Trying to pass without redirect uri parameter in form',
                form=Remove('redirectUri')
            )
            assert status == '766 Redirect Uri Not In form'

            when(
                'The user already in this organization',
                form=Update(email=self.member2.email)
            )
            assert status == '628 Already In This Organization'

            self.logout()
            self.login(email=self.member2.email)
            when(
                'The user is not the owner of the organization',
                form=Update(email=self.member2.email),
                authorization=self._authentication_token,
            )
            assert status == 403

            when('Trying with an unauthorized member', authorization=None)
            assert status == 401

