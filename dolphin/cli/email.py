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
            help='Email to be invite'
        )
        parser.add_argument(
            '-o',
            '--organization',
            required=True,
            help='Organization is invited'
        )
        parser.add_argument(
            '-m',
            '--member',
            required=True,
            help='Member id'
        )
        parser.add_argument(
            '-w',
            '--owner',
            required=True,
            help='Owner id'
        )
        parser.add_argument(
            '-r',
            '--role',
            required=True,
            help='role'
        )

        return parser

    def launch(self):
        token = OrganizationInvitationToken(dict(
            email=self.args.email,
            organizationId=self.args.organization,
            memberReferenceId=self.args.member,
            ownerReferenceId=self.args.owner,
            role=self.args.role,
        ))
        email = OrganizationInvitationEmail(
            to=self.args.email,
            subject='Invite to organization',
            body={
                'token': token.dump(),
                'callback_url':
                    settings.organization_invitation.callback_url,
                'state': self.args.organization,
                'email': self.args.email,
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

