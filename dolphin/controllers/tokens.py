from nanohttp import RestController, json, context, HTTPBadRequest, validate
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit
from sqlalchemy import exists, and_

from ..backends import CASClient, ChatClient
from ..models import Member, Invitation, OrganizationMember
from ..validators import token_obtain_validator, USER_EMAIL_PATTERN
from ..exceptions import StatusEmailNotInForm, StatusInvalidEmailFormat, \
    StatusIncorrectEMailOrPassword


class TokenController(RestController):

    def _ensure_organization(self, member):
        organization_id = context.form.get('organizationId')

        is_member_in_organization = DBSession.query(exists().where(and_(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.member_id == member.id
        ))).scalar()

        if is_member_in_organization:
            return organization_id

        invitation = DBSession.query(Invitation) \
            .filter(
                Invitation.email == member.email,
                Invitation.organization_id == organization_id
            ) \
            .one_or_none()

        if invitation is None:
            raise HTTPBadRequest()

        organization_member = OrganizationMember(
            organization_id=invitation.organization_id,
            member_id=member.id,
            role=invitation.role,
        )
        DBSession.add(organization_member)
        return organization_id

    @authorize
    @json
    def invalidate(self):
        context.application.__authenticator__.logout()
        return {}

    @json(prevent_empty_form=True)
    @validate(
        email=dict(
            required=StatusEmailNotInForm,
            pattern=(USER_EMAIL_PATTERN, StatusInvalidEmailFormat)
        )
    )
    def create(self):
        email = context.form.get('email')
        password = context.form.get('password')
        if email and password is None:
            raise StatusIncorrectEMailOrPassword()

        principal = context.application.__authenticator__.\
            login((email, password))

        if principal is None:
            raise StatusIncorrectEMailOrPassword()

        return dict(token=principal.dump())

