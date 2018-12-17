from nanohttp import RestController, json, context, HTTPBadRequest, validate, \
    settings
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit
from sqlalchemy import exists, and_

from ..backends import CASClient, ChatClient
from ..models import Member, Invitation, OrganizationMember
from ..validators import token_obtain_validator


class TokenController(RestController):

    def _ensure_organization(self, member):
        organization_id = context.form.get('organizationId')

        is_member_in_organization = DBSession.query(exists().where(and_(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.member_reference_id == member.reference_id
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
            member_reference_id=member.reference_id,
            role=invitation.role,
        )
        DBSession.add(organization_member)
        return organization_id


    @validate(
        email=dict(
            required='400 Invalid email or password'
        ),
    )
    @json
    def create(self):
        email = context.form.get('email')
        principal = context.application.__authenticator__.login(email)
        if principal is None:
            raise HTTPBadRequest('Invalid email or password')
        return dict(token=principal.dump())

    @authorize
    @json
    def invalidate(self):
        context.application.__authenticator__.logout()
        return {}

    @json(prevent_form='711 Form Not Allowed')
    def request(self):
        return dict(
            scopes=['email', 'title'],
            applicationId=settings.oauth['application_id'],
        )

    @json
    @token_obtain_validator
    @commit
    def obtain(self):
        cas_client = CASClient()

        access_token, ___ = cas_client \
            .get_access_token(context.form.get('authorizationCode'))

        cas_member = cas_client.get_member(access_token)
        member = DBSession.query(Member) \
            .filter(Member.reference_id == cas_member['id']) \
            .one_or_none()

        if member is None:

            member = Member(
                reference_id=cas_member['id'],
                email=cas_member['email'],
                title=cas_member['title'],
                access_token=access_token
            )
            DBSession.add(member)

        if member.title != cas_member['title']:
            member.title = cas_member['title']

        if member.avatar != cas_member['avatar']:
            member.avatar = cas_member['avatar']

        if member.name != cas_member['name']:
            member.name = cas_member['name']

        if member.access_token != 'access_tokne':
            member.access_token = access_token

        DBSession.flush()
        principal = context.application.__authenticator__.login(member.email)

        organization_id = self._ensure_organization(member)
        principal.payload['organizationId'] = organization_id
        token = principal.dump().decode('utf-8')

        ensured_member = ChatClient().ensure_member(token, member.access_token)
        return dict(token=token)

