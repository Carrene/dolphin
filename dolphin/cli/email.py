from nanohttp import settings
from easycli import SubCommand, Argument

from ..models import OrganizationInvitationEmail
from ..tokens import OrganizationInvitationToken


class SendEmailLauncher(SubCommand):  # pragma: no cover
    __help__ = 'Sends an email.'
    __command__ = 'send'
    __arguments__ = [
        Argument(
            '-e',
            '--email',
            required=True,
            help='Invitation email'
        ),
        Argument(
            '-o',
            '--organization_id',
            required=True,
            help='Organization id'
        ),
        Argument(
            '-i',
            '--inviter_id',
            required=True,
            help='By member'
        ),
        Argument(
            '-r',
            '--role',
            required=True,
            help='role'
        ),
        Argument(
            '-u',
            '--redirect_uri',
            required=True,
            help='Redirect uri'
        ),
    ]

    def __call__(self, args):
        token = OrganizationInvitationToken(dict(
            email=self.args.email,
            organizationId=self.args.organization_id,
            byMemberReferenceId=self.args.inviter_id,
            role=self.args.role,
        ))
        email = OrganizationInvitationEmail(
            to=self.args.email,
            subject='Invite to organization',
            body={
                'token': token.dump().decode('utf-8'),
                'callback_url':
                    settings.organization_invitation.callback_url,
                'state': self.args.organization_id,
                'email': self.args.email,
                'application_id': 1,
                'scopes': 'title,email,name,phone,avatar',
                'redirect_uri': self.args.redirect_uri,
            }
        )
        email.to = self.args.email
        email.do_({})


class EmailLauncher(SubCommand):  # pragma: no cover
    __help__ = 'Manage emails.'
    __command__ = 'email'
    __arguments__ = [
        SendEmailLauncher,
    ]

