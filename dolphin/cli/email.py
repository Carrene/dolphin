from easycli import SubCommand, Argument
from nanohttp import settings

from ..models import OrganizationInvitationEmail
from ..tokens import OrganizationInvitationToken


class SendEmailSubSubCommand(SubCommand):  # pragma: no cover
    __help__ = 'Sends an email.'
    __command__ = 'send'
    __arguments__ = [
        Argument(
            '-e',
            '--email',
            required=True,
            help='Invitation email',
        ),
        Argument(
            '-o',
            '--organization_id',
            required=True,
            help='Organization id',
        ),
        Argument(
            '-i',
            '--inviter_id',
            required=True,
            help='By member',
        ),
        Argument(
            '-r',
            '--role',
            required=True,
            help='role',
        ),
        Argument(
            '-u',
            '--redirect_uri',
            required=True,
            help='Redirect uri',
        ),
    ]

    def __call__(self, args):
        token = OrganizationInvitationToken(dict(
            email=args.email,
            organizationId=args.organization_id,
            byMemberReferenceId=args.inviter_id,
            role=args.role,
        ))
        email = OrganizationInvitationEmail(
            to=args.email,
            subject='Invite to organization',
            body={
                'token': token.dump().decode('utf-8'),
                'callback_url':
                    settings.organization_invitation.callback_url,
                'state': args.organization_id,
                'email': args.email,
                'application_id': 1,
                'scopes': 'title,email,name,phone,avatar',
                'redirect_uri': args.redirect_uri,
            }
        )
        email.to = args.email
        email.do_({})


class EmailSubCommand(SubCommand):  # pragma: no cover
    __help__ = 'Manage emails.'
    __command__ = 'email'
    __arguments__ = [
        SendEmailSubSubCommand,
    ]

