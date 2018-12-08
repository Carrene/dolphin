from nanohttp import context, json, HTTPNotFound, HTTPForbidden, settings
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import commit, DBSession
from sqlalchemy import exists, and_
from sqlalchemy_media import store_manager

from ..exceptions import HTTPRepetitiveTitle
from ..models import Member, Organization, OrganizationMember, OrganizationInvitationEmail
from ..tokens import OrganizationInvitationToken
from ..validators import token_validator, organization_create_validator, \
    organization_title_validator, organization_domain_validator, \
    organization_url_validator, email_validator, organization_role_validator


class OrganizationController(ModelRestController):
    __model__ = Organization

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

