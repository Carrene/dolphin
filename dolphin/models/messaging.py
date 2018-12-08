from restfulpy.messaging import Email


class OrganizationInvitationEmail(Email):
    __mapper_args__ = {
        'polymorphic_identity': 'organization_invitation_email'
    }

    template_filename = 'organization_invitation_email.mako'

