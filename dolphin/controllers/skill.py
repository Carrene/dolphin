from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import Skill
from ..validators import skill_create_validator


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

