from nanohttp import json, int_or_notfound , HTTPNotFound, context, HTTPStatus
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import Skill, SkillMember
from ..exceptions import StatusAlreadyGrantedSkill, StatusSkillNotGrantedYet, \
    StatusRepetitiveTitle
from ..validators import skill_create_validator, skill_update_validator


FORM_WHITELIST = [
    'title',
    'description',
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class SkillController(ModelRestController):
    __model__ = Skill

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @skill_create_validator
    @commit
    def create(self):
        skill = Skill()
        skill.update_from_request()
        DBSession.add(skill)
        return skill

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @skill_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        skill = DBSession.query(Skill).get(id)

        if DBSession.query(Skill) \
                .filter(
                    Skill.title == context.form['title'],
                    Skill.id != id
                ) \
                .one_or_none():
            raise StatusRepetitiveTitle()

        if skill is None:
            raise HTTPNotFound()

        skill.update_from_request()
        DBSession.add(skill)
        return skill

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        skill = DBSession.query(Skill).get(id)
        if skill is None:
            raise HTTPNotFound()

        return skill

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Skill.expose
    def list(self):
        return DBSession.query(Skill)

