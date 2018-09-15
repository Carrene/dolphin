from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case
from restfulpy.controllers import ModelRestController

from ..models import Project, Subscription
from ..validators import project_validator, update_project_validator, \
    subscribe_validator


class ProjectController(ModelRestController):
    __model__ = Project

    @authorize
    @json
    @project_validator
    @Project.expose
    @commit
    def create(self):
        title = context.form['title']
        project = DBSession.query(Project) \
            .filter(Project.title == title) \
            .one_or_none()
        project = Project()
        project.update_from_request()
        DBSession.add(project)
        return project

    @authorize
    @json(prevent_empty_form='708 No Parameter Exists In The Form')
    @update_project_validator
    @Project.expose
    @commit
    def update(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        # FIXME: these lines should be removed and replaced by Project.validate
        # decorator
        json_columns = set(
            c.info.get('json', to_camel_case(c.key)) for c in
            Project.iter_json_columns(include_readonly_columns=False)
        )
        if set(form.keys()) - json_columns:
            raise HTTPStatus(
                f'707 Invalid field, only one of '
                f'"{", ".join(json_columns)}" is accepted'
            )

        project.update_from_request()
        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def hide(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        project.soft_delete()
        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def show(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        project.soft_undelete()
        return project

    @authorize
    @json
    @Project.expose
    def list(self):

        query = DBSession.query(Project)
        return query

    @authorize
    @json
    @subscribe_validator
    @Project.expose
    @commit
    def subscribe(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        if DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none():
            raise HTTPStatus('611 Already Subscribed')

        subscription = Subscription(
            subscribable=id,
            member=form['memberId']
        )
        DBSession.add(subscription)

        return project

    @authorize
    @json
    @subscribe_validator
    @Project.expose
    @commit
    def unsubscribe(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none()
        if not subscription:
            raise HTTPStatus('612 Not Subscribed Yet')

        DBSession.delete(subscription)

        return project

