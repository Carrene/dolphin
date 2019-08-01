from nanohttp import json, int_or_notfound, HTTPNotFound, context
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..exceptions import StatusRepetitiveTitle
from ..models import Specialty
from ..validators import specialty_create_validator, specialty_update_validator


FORM_WHITELIST = [
    'title',
    'description',
    'skillId',
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class SpecialtyController(ModelRestController):
    __model__ = Specialty

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @specialty_create_validator
    @commit
    def create(self):
        specialty = Specialty()
        specialty.update_from_request()
        DBSession.add(specialty)
        return specialty

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @specialty_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        specialty = DBSession.query(Specialty).get(id)
        if specialty is None:
            raise HTTPNotFound()

        if DBSession.query(Specialty) \
                .filter(
                    Specialty.title == context.form['title'],
                    Specialty.id != id
                ) \
                .one_or_none():
            raise StatusRepetitiveTitle()

        specialty.update_from_request()
        DBSession.add(specialty)
        return specialty

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        specialty = DBSession.query(Specialty).get(id)
        if specialty is None:
            raise HTTPNotFound()

        return specialty

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Specialty.expose
    def list(self):
        return DBSession.query(Specialty)

