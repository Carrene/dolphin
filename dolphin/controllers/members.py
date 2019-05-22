from nanohttp import json, HTTPNotFound, context, HTTPUnauthorized, \
    int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy_media import store_manager
from sqlalchemy import or_

from ..tokens import RegistrationToken
from ..models import Member, Skill, SkillMember, Organization, \
    OrganizationMember, Group, GroupMember
from ..exceptions import StatusAlreadyGrantedSkill, StatusSkillNotGrantedYet, \
    StatusQueryParameterNotInFormOrQueryString, \
    StatusTitleAlreadyRegistered, StatusEmailAddressAlreadyRegistered
from ..validators import search_member_validator, register_member_validator
from .organization import OrganizationController
from .skill import SkillController


class MemberController(ModelRestController):
    __model__ = Member

    def __call__(self, *remaining_paths):

        if len(remaining_paths) > 1 and remaining_paths[1] == 'organizations':
            if not context.identity:
                raise HTTPUnauthorized()

            id = int_or_notfound(remaining_paths[0])
            member = DBSession.query(Member).get(id)
            if member is None \
                    or member.id != context.identity.id:
                raise HTTPNotFound()

            return MemberOrganizationController(member=member) \
                (*remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'skills':

            id = int_or_notfound(remaining_paths[0])
            member = DBSession.query(Member).get(id)
            if member is None:
                raise HTTPNotFound()

            return MemberSkillController(member=member)(*remaining_paths[2:])

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

    @json(prevent_empty_form=True)
    @register_member_validator
    @Member.expose
    @commit
    def register(self):
        title = context.form.get('title')
        password = context.form.get('password')
        ownership_token = context.form.get('ownershipToken')
        registration_token_principal = RegistrationToken.load(ownership_token)
        email = registration_token_principal.email

        if DBSession.query(Member.title).filter(Member.title == title).count():
            raise StatusTitleAlreadyRegistered()

        if DBSession.query(Member.email).filter(Member.email == email).count():
            raise StatusEmailAddressAlreadyRegistered()

        member = Member(
            email=email,
            title=title,
            password=password,
            role='member'
        )
        DBSession.add(member)
        DBSession.flush()
        principal = member.create_jwt_principal()
        context.application.__authenticator__.setup_response_headers(principal)
        return member


class MemberSkillController(ModelRestController):
    __model__ = Skill

    def __init__(self, member):
        self.member = member

    @authorize
    @json
    @commit
    def grant(self, id):
        id = int_or_notfound(id)
        skill = DBSession.query(Skill).get(id)
        if skill is None:
            raise HTTPNotFound()

        if DBSession.query(SkillMember) \
                .filter(
                    SkillMember.skill_id == id,
                    SkillMember.member_id == self.member.id
                ) \
                .one_or_none():
            raise StatusAlreadyGrantedSkill()

        skill_member = SkillMember(
            skill_id=id,
            member_id=self.member.id,
        )
        DBSession.add(skill_member)
        return skill

    @authorize
    @json
    @commit
    def deny(self, id):
        id = int_or_notfound(id)
        skill = DBSession.query(Skill).get(id)
        if skill is None:
            raise HTTPNotFound()

        if not DBSession.query(SkillMember) \
                .filter(
                    SkillMember.skill_id == id,
                    SkillMember.member_id == self.member.id
                ) \
                .one_or_none():
            raise StatusSkillNotGrantedYet()

        skill.members.remove(self.member)
        return skill

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Skill.expose
    def list(self):
        return DBSession.query(Skill) \
            .join(SkillMember, Skill.id == SkillMember.skill_id) \
            .filter(SkillMember.member_id == self.member.id)


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

