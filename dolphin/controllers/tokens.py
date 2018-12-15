from nanohttp import RestController, json, context, HTTPBadRequest, validate, \
    settings
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit

from ..backends import CASClient
from ..models import Member


class TokenController(RestController):

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

        if member.access_token != access_token:
            member.access_token = access_token

        DBSession.flush()
        principal = context.application.__authenticator__.login(member.email)
        context.response_headers.add_header(
            'X-New-JWT-Token',
            principal.dump().decode('utf-8')
        )

        return dict(token=principal.dump().decode('utf-8'))

