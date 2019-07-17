from nanohttp import json, HTTPNotFound, context, HTTPUnauthorized, \
    int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy_media import store_manager
from sqlalchemy import or_

from ..models import Member, Specialty, SpecialtyMember, Organization, \
    OrganizationMember, Group, GroupMember
from ..exceptions import StatusAlreadyGrantedSpecialty, StatusSpecialtyNotGrantedYet, \
    StatusQueryParameterNotInFormOrQueryString
from ..validators import search_member_validator
from .organization import OrganizationController
from .specialty import SpecialtyController


class MemberController(ModelRestController):
    __model__ = Member

    def __call__(self, *remaining_paths):

        if len(remaining_paths) > 1 and remaining_paths[1] == 'organizations':
            if not context.identity:
                raise HTTPUnauthorized()

            id = int_or_notfound(remaining_paths[0])
            member = DBSession.query(Member).get(id)
            if member is None \
                    or member.reference_id != context.identity.reference_id:
                raise HTTPNotFound()

            return MemberOrganizationController(member=member) \
                (*remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'specialtys':

            id = int_or_notfound(remaining_paths[0])
            member = DBSession.query(Member).get(id)
            if member is None:
                raise HTTPNotFound()

            return MemberSpecialtyController(member=member)(*remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'groups':
            id = int_or_notfound(remaining_paths[0])
            member = DBSession.query(Member).get(id)
            if member is None:
                raise HTTPNotFound()

            return MemberGroupController(member=member)(*remaining_paths[2:])

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
        id = int_or_notfound(id)

        member = DBSession.query(Member).get(id)
        if not member:
            raise HTTPNotFound()

        return member

    @authorize
    @search_member_validator
    @json
    @Member.expose
    def search(self):
        query = context.form.get('query') or context.query.get('query')
        if query is None:
            raise StatusQueryParameterNotInFormOrQueryString()

        query = f'%{query}%'
        query = DBSession.query(Member) \
            .filter(or_(
                Member.title.ilike(query),
                Member.name.ilike(query)
            ))

        return query


class MemberSpecialtyController(ModelRestController):
    __model__ = Specialty

    def __init__(self, member):
        self.member = member

    @authorize
    @json
    @commit
    def grant(self, id):
        id = int_or_notfound(id)
        specialty = DBSession.query(Specialty).get(id)
        if specialty is None:
            raise HTTPNotFound()

        if DBSession.query(SpecialtyMember) \
                .filter(
                    SpecialtyMember.specialty_id == id,
                    SpecialtyMember.member_id == self.member.id
                ) \
                .one_or_none():
            raise StatusAlreadyGrantedSpecialty()

        specialty_member = SpecialtyMember(
            specialty_id=id,
            member_id=self.member.id,
        )
        DBSession.add(specialty_member)
        return specialty

    @authorize
    @json
    @commit
    def deny(self, id):
        id = int_or_notfound(id)
        specialty = DBSession.query(Specialty).get(id)
        if specialty is None:
            raise HTTPNotFound()

        if not DBSession.query(SpecialtyMember) \
                .filter(
                    SpecialtyMember.specialty_id == id,
                    SpecialtyMember.member_id == self.member.id
                ) \
                .one_or_none():
            raise StatusSpecialtyNotGrantedYet()

        specialty.members.remove(self.member)
        return specialty

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Specialty.expose
    def list(self):
        return DBSession.query(Specialty) \
            .join(SpecialtyMember, Specialty.id == SpecialtyMember.specialty_id) \
            .filter(SpecialtyMember.member_id == self.member.id)


class MemberOrganizationController(ModelRestController):
    __model__ = Organization

    def __init__(self, member):
        self.member = member

    @store_manager(DBSession)
    @json(prevent_form=True)
    @Organization.expose
    def list(self):
        return DBSession.query(Organization) \
            .join(
                OrganizationMember,
                OrganizationMember.member_id == self.member.id
            )


class MemberGroupController(ModelRestController):
    __model__ = Group

    def __init__(self, member):
        self.member = member

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Group.expose
    def list(self):
        return DBSession.query(Group) \
            .join(GroupMember, GroupMember.group_id == Group.id) \
            .filter(GroupMember.member_id == self.member.id)

