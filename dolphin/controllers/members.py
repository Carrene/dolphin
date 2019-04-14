from nanohttp import json, HTTPNotFound, context, HTTPUnauthorized, \
    int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy_media import store_manager

from ..models import Member, Skill, SkillMember, Organization, \
    OrganizationMember
from ..exceptions import HTTPAlreadyGrantedSkill, HTTPSkillNotGrantedYet
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
            raise HTTPAlreadyGrantedSkill()

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
            raise HTTPSkillNotGrantedYet()

        skill.members.remove(self.member)
        return skill


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

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Skill.expose
    def list(self):
        return DBSession.query(Skill) \
            .join(SkillMember, Skill.id == SkillMember.skill_id) \
            .filter(SkillMember.member_id == self.member.id)

