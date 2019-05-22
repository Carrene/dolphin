from nanohttp import settings
from restfulpy.cli import Launcher, RequireSubCommand

from ..models import OrganizationInvitationEmail
from ..tokens import OrganizationInvitationToken


class SendEmailLauncher(Launcher):  # pragma: no cover

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('send', help='Sends an email.')
        parser.add_argument(
            '-e',
            '--email',
            required=True,
            help='Invitation email'
        )
        parser.add_argument(
            '-o',
            '--organization_id',
            required=True,
            help='Organization id'
        )
        parser.add_argument(
            '-i',
            '--inviter_id',
            required=True,
            help='By member'
        )
        parser.add_argument(
            '-r',
            '--role',
            required=True,
            help='role'
        )
        parser.add_argument(
            '-u',
            '--redirect_uri',
            required=True,
            help='Redirect uri'
        )

        return parser

    def launch(self):
        token = OrganizationInvitationToken(dict(
            email=self.args.email,
            organizationId=self.args.organization_id,
            byMemberId=self.args.inviter_id,
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


class EmailLauncher(Launcher, RequireSubCommand):  # pragma: no cover

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('email', help="Manage emails")
        user_subparsers = parser.add_subparsers(
            title="Email managements",
            dest="email_command"
        )
        SendEmailLauncher.register(user_subparsers)
        return parser

