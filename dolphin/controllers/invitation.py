from datetime import datetime, timedelta

from nanohttp import context, json, HTTPForbidden, settings
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController, JSONPatchControllerMixin
from restfulpy.orm import commit, DBSession
from sqlalchemy import exists, and_
from sqlalchemy_media import store_manager

from ..exceptions import StatusAlreadyInThisOrganization
from ..models import Member, Organization, OrganizationMember, \
    OrganizationInvitationEmail, Invitation
from ..tokens import OrganizationInvitationToken
from ..validators import organization_invite_validator


class InvitationController(ModelRestController, JSONPatchControllerMixin):
    __model__ = Invitation

    def __init__(self, organization=None):
        self.organization = organization

    @authorize
    @store_manager(DBSession)
    @organization_invite_validator
    @json(prevent_empty_form=True)
    @Organization.expose
    @commit
    def create(self):
        email = context.form.get('email')
        role = context.form.get('role')
        application_id = context.form.get('applicationId')
        scopes = context.form.get('scopes')
        redirect_uri = context.form.get('redirectUri')
        by_member = Member.current()

        organization_member = DBSession.query(OrganizationMember) \
            .filter(and_(
                OrganizationMember.organization_id == self.organization.id,
                OrganizationMember.member_id == by_member.id
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
                OrganizationMember.member_id == invited_member.id
            ))).scalar()
            if is_member_in_organization:
                raise StatusAlreadyInThisOrganization()

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
            DBSession.add(invitation)

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
                    'application_id': application_id,
                    'scopes': scopes,
                    'redirect_uri': redirect_uri,
                }
            )
        )
        return invitation

