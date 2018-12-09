from nanohttp import json, HTTPNotFound, context, HTTPUnauthorized
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Member
from .organization import OrganizationController


class MemberController(ModelRestController):
    __model__ = Member

    def __call__(self, *remaining_paths):

        if len(remaining_paths) > 1 and remaining_paths[1] == 'organizations':
            if not context.identity:
                raise HTTPUnauthorized()

            try:
                id = int(remaining_paths[0])

            except (ValueError, TypeError):
                raise HTTPNotFound()

            member = DBSession.query(Member) \
                .filter(Member.id == id) \
                .one_or_none()

            if member is None \
                    or member.reference_id != context.identity.reference_id:
                raise HTTPNotFound()

            return OrganizationController(member=member)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    @authorize
    @json
    @Member.expose
    def list(self):
        query = DBSession.query(Member)
        return query

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Member.expose
    def get(self, id):

        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        member = DBSession.query(Member).filter(Member.id == id).one_or_none()
        if not member:
            raise HTTPNotFound()

        return member

