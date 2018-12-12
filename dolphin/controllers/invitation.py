from datetime import datetime, timedelta

from nanohttp import context, json, HTTPForbidden, settings
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import commit, DBSession
from sqlalchemy import exists, and_
from sqlalchemy_media import store_manager

from ..exceptions import HTTPAlreadyInThisOrganization
from ..models import Member, Organization, OrganizationMember, \
    OrganizationInvitationEmail, Invitation
from ..tokens import OrganizationInvitationToken
from ..validators import organization_invite_validator


class InvitationController(ModelRestController):
    __model__ = Organization

    def __init__(self, organization=None):
        self.organization = organization

    @authorize
    @store_manager(DBSession)
<<<<<<< HEAD
    @organization_invite_validator
    @json(prevent_empty_form=True)
=======
    @json(prevent_empty_form=True)
    @organization_invite_validator
>>>>>>> Implementing the create method for the invitation controller, closes #264
    @Organization.expose
    @commit
    def create(self):
        email = context.form.get('email')
        role = context.form.get('role')
        by_member = Member.current()

        organization_member = DBSession.query(OrganizationMember) \
            .filter(and_(
                OrganizationMember.organization_id == self.organization.id,
                OrganizationMember.member_reference_id == by_member.reference_id
            )) \
            .one_or_none()
        if organization_member is None or organization_member.role != 'owner':
            raise HTTPForbidden()

        email = context.form.get('email')
        invited_member = DBSession.query(Member) \
            .filter(Member.email == email) \
            .one_or_none()
        if invited_member is not None:
            is_member_in_organization = DBSession.query(exists().where(and_(
                OrganizationMember.organization_id == self.organization.id,
                OrganizationMember.member_reference_id \
                    == invited_member.reference_id
            ))).scalar()
            if is_member_in_organization:
                raise HTTPAlreadyInThisOrganization()

        invitation = DBSession.query(Invitation) \
            .filter(Invitation.email == email) \
            .one_or_none()
        if invitation is None:
            invitation = Invitation(
                email=email,
                organization_id=self.organization.id,
                by_member_id=by_member.id,
                role=role,
                expired_date=datetime.now() + timedelta(days=1),
                accepted=False
            )
<<<<<<< HEAD
            DBSession.add(invitation)
=======
>>>>>>> Implementing the create method for the invitation controller, closes #264

        token = OrganizationInvitationToken(dict(
            email=email,
            organizationId=self.organization.id,
            byMemberReferenceId=context.identity.reference_id,
            role=role,
        ))
        DBSession.add(
            OrganizationInvitationEmail(
                to=email,
                subject='Invite to organization',
                body={
                    'token': token.dump(),
                    'callback_url':
                        settings.organization_invitation.callback_url,
                    'state': self.organization.id,
                    'email': email,
                }
            )
        )
        return invitation

