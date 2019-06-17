from nanohttp import json, HTTPNotFound, context, HTTPUnauthorized, \
    int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy_media import store_manager
from sqlalchemy import or_

from ..models import Member, Skill, SkillMember, Organization, \
    OrganizationMember, Group, GroupMember
from ..exceptions import StatusAlreadyGrantedSkill, StatusSkillNotGrantedYet, \
    StatusQueryParameterNotInFormOrQueryString
from ..validators import search_member_validator, member_register_validator, \
    member_update_validator
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
                    or member.reference_id != context.identity.reference_id:
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
    @member_register_validator
    @commit
    def register(self):
        title = context.form.get('title')
        password = context.form.get('password')
        ownership_token = context.form.get('ownershipToken')
        regitration_token_principal = RegistrationToken.load(ownership_token)
        email = regitration_token_principal.email

        if DBSession.query(Member.title).filter(Member.title == title).count():
            raise HTTPTitleAlreadyRegistered()

        if DBSession.query(Member.email).filter(Member.email == email).count():
            raise HTTPEmailAddressAlreadyRegistered()

        member = Member(
            email=email,
            title=title,
            password=password,
            name=context.form.get('name'),
            role='member'
        )
        DBSession.add(member)
        DBSession.flush()
        principal = member.create_jwt_principal()
        context.application.__authenticator__.setup_response_headers(principal)
        return member

    @store_manager(DBSession)
    @authorize
    @json
    @Member.expose
    def get(self, id_):
        id_ = context.identity.id if id_ == 'me' else id_
        id_ = int_or_notfound(id_)

        member = DBSession.query(Member).get(id_)
        if not member:
            raise HTTPNotFound()

        if member.id != context.identity.id:
            context.identity.assert_roles('admin')

        return member

    @store_manager(DBSession)
    @authorize
    @json(
        form_whitelist=(
            ['name', 'avatar'],
            '717 Invalid field, only the name and avatar parameters are ' \
            'accepted'
        ),
        prevent_empty_form=True
    )
    @member_update_validator
    @Member.expose
    @commit
    def update(self, id):
        id = int_or_notfound(id)

        member = DBSession.query(Member).get(id)
        if member is None:
            raise HTTPNotFound()

        if member.id != context.identity.reference_id:
            raise HTTPNotFound()

        member.update_from_request()
        context.application.__authenticator__.invalidate_member(member.id)
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

