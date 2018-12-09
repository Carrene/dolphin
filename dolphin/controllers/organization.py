from nanohttp import context, json, HTTPForbidden, HTTPNotFound, settings
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import commit, DBSession
from sqlalchemy import exists, and_
from sqlalchemy_media import store_manager

from ..exceptions import HTTPRepetitiveTitle, HTTPAlreadyInThisOrganization
from ..models import Member, Organization, OrganizationMember, \
    OrganizationInvitationEmail
from ..tokens import OrganizationInvitationToken
from ..validators import organization_create_validator, \
    organization_invite_validator, organization_join_validator


class OrganizationController(ModelRestController):
    __model__ = Organization

    def __init__(self, member=None):
        self.member = member

    @authorize
    @json(prevent_empty_form=True)
    @organization_create_validator
    @Organization.expose
    @commit
    def create(self):
        organization = DBSession.query(Organization) \
            .filter(Organization.title == context.form.get('title')) \
            .one_or_none()
        if organization is not None:
            raise HTTPRepetitiveTitle()

        member = Member.current()
        organization = Organization(
            title=context.form.get('title'),
        )
        DBSession.add(organization)
        DBSession.flush()

        organization_member = OrganizationMember(
            organization_id=organization.id,
            member_reference_id=member.reference_id,
            role='owner',
        )
        DBSession.add(organization_member)
        return organization

    @authorize
    @store_manager(DBSession)
    @json(prevent_empty_form=True)
    @organization_invite_validator
    @Organization.expose
    @commit
    def invite(self, id):
        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        organization = DBSession.query(Organization).get(id)
        if organization is None:
            raise HTTPNotFound()

        email = context.form.get('email')
        member = DBSession.query(Member) \
            .filter(Member.email == email) \
            .one_or_none()
        if member is None:
            raise HTTPNotFound()

        organization_member = DBSession.query(OrganizationMember) \
            .filter(
                OrganizationMember.organization_id == id,
                OrganizationMember.member_reference_id == \
                    context.identity.reference_id
            ) \
            .one_or_none()
        if organization_member is None or organization_member.role != 'owner':
            raise HTTPForbidden()

        is_member_in_organization = DBSession.query(exists().where(and_(
            OrganizationMember.organization_id == id,
            OrganizationMember.member_reference_id == member.reference_id
        ))).scalar()
        if is_member_in_organization:
            raise HTTPAlreadyInThisOrganization()

        token = OrganizationInvitationToken(dict(
            email=email,
            organizationId=id,
            memberReferenceId=member.reference_id,
            ownerReferenceId=context.identity.reference_id,
            role=context.form.get('role'),
        ))
        DBSession.add(
            OrganizationInvitationEmail(
                to=email,
                subject='Invite to organization',
                body={
                    'token': token.dump(),
                    'callback_url':
                        settings.organization_invitation.callback_url
                }
            )
        )
        return organization

    @authorize
    @store_manager(DBSession)
    @json(prevent_empty_form=True)
    @organization_join_validator
    @commit
    def join(self):
        token = OrganizationInvitationToken.load(context.form.get('token'))
        organization = DBSession.query(Organization).get(token.organization_id)
        if organization is None:
            raise HTTPNotFound()

        is_member_in_organization = DBSession.query(
            exists() \
            .where(
                OrganizationMember.organization_id == token.organization_id
            ) \
            .where(
                OrganizationMember.member_reference_id == \
                    token.member_reference_id
            )
        ).scalar()
        if is_member_in_organization:
            raise HTTPAlreadyInThisOrganization()

        organization_member = OrganizationMember(
            member_reference_id=token.member_reference_id,
            organization_id=organization.id,
            role=token.role,
        )
        DBSession.add(organization_member)
        return organization

    @store_manager(DBSession)
    @json
    @Organization.expose
    @commit
    def list(self):

        if self.member is not None:
            return DBSession.query(Organization).join(
                OrganizationMember,
                OrganizationMember.organization_id == Organization.id
            ).filter(
                OrganizationMember.member_reference_id == self.member.reference_id
            )

        if 'email' in context.form.keys():
            return DBSession.query(Organization) \
                .join(
                    OrganizationMember,
                    OrganizationMember.organization_id == Organization.id
                ) \
                .join(
                    Member,
                    Member.reference_id \
                        == OrganizationMember.member_reference_id
                ) \
                .filter(Member.email == context.form.get('email'))

        else:
            return DBSession.query(Organization)

