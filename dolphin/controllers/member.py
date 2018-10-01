from nanohttp import RestController, json, context
from restfulpy.orm import DBSession, commit

from ..backends import CASClient
from ..models import Member


class MemberController(RestController):

    @json
    @commit
    def obtain(self):
        access_token, member_id = CASClient() \
            .get_access_token(context.form.get('authorizationCode'))

        cas_member = CASClient().get_member(access_token)
        member = DBSession.query(Member) \
            .filter(Member.email == cas_member['email']) \
            .one_or_none()

        if member is None:
            member = Member(
                reference_id=cas_member['id'],
                email=cas_member['email'],
                title=cas_member['title'],
                access_token=access_token
            )
        else:
            member.access_token = access_token

        DBSession.add(member)
        return member

