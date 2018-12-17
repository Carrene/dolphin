from nanohttp import context, json, HTTPForbidden, HTTPNotFound, settings, \
    HTTPUnauthorized
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import commit, DBSession
from sqlalchemy import exists, and_
from sqlalchemy_media import store_manager

from ..exceptions import HTTPRepetitiveTitle, HTTPAlreadyInThisOrganization
from ..models import Member, Organization, OrganizationMember, \
    OrganizationInvitationEmail, AbstractOrganizationMemberView
from ..tokens import OrganizationInvitationToken
from ..validators import organization_create_validator, \
    organization_invite_validator
from .invitation import InvitationController


OrganizationMemberView = AbstractOrganizationMemberView.create_mapped_class()


class OrganizationController(ModelRestController):
    __model__ = Organization

    def __init__(self, member=None):
        self.member = member

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1:

            if not context.identity:
                raise HTTPUnauthorized()

            try:
                id = int(remaining_paths[0])

            except (ValueError, TypeError):
                raise HTTPNotFound()

            member = Member.current()
            organization = DBSession.query(Organization) \
               .filter(Organization.id == id) \
               .join(
                   OrganizationMember,
                   OrganizationMember.member_id == member.id
               ) \
               .one_or_none()
            if organization is None:
                raise HTTPNotFound()

            if remaining_paths[1] == 'organizationmembers':
                return OrganizationMemberController(organization=organization) \
                    (*remaining_paths[2:])
            elif remaining_paths[1] == 'invitations':
                return InvitationController(organization=organization) \
                    (*remaining_paths[2:])

        return super().__call__(*remaining_paths)

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
            member_id=member.id,
            role='owner',
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
            ).filter(OrganizationMember.member_id == self.member.id)

        if 'email' in context.form.keys():
            return DBSession.query(Organization) \
                .join(
                    OrganizationMember,
                    OrganizationMember.organization_id == Organization.id
                ) \
                .join(
                    Member,
                    Member.id == OrganizationMember.member_id
                ) \
                .filter(Member.email == context.form.get('email'))

        else:
            return DBSession.query(Organization)

    @authorize
    @store_manager(DBSession)
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        try:
            id = int(id)

        except (ValueError, TypeError):
            raise HTTPNotFound()

        member = Member.current()
        organization = DBSession.query(Organization) \
           .filter(Organization.id == id) \
           .join(
               OrganizationMember,
               OrganizationMember.member_id == member.id
           ) \
           .one_or_none()

        if organization is None:
            raise HTTPNotFound()

        return organization


class OrganizationMemberController(ModelRestController):
    __model__ = OrganizationMemberView

    def __init__(self, organization=None):
        self.organization = organization

    @authorize
    @store_manager(DBSession)
    @json(prevent_form=True)
    @OrganizationMemberView.expose
    @commit
    def list(self):
        query = DBSession.query(OrganizationMemberView).filter(
            OrganizationMemberView.organization_id == self.organization.id
        )
        return query

