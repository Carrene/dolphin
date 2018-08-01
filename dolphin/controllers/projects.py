from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case
from restfulpy.controllers import ModelRestController

from dolphin.models import Project, project_statuses, project_phases
from dolphin.validators import project_validator, update_project_validator


class ProjectController(ModelRestController):
    __model__ = Project

    @json
    @project_validator
    @Project.expose
    @commit
    def create(self):
        title = context.form['title']
        project = DBSession.query(Project).filter_by(title=title) \
            .one_or_none()

        if project is not None:
            raise HTTPStatus(
                f'600 A project with title: {title} is already exists.'
            )

        project = Project()
        project.update_from_request()
        DBSession.add(project)
        return project

    @json
    @update_project_validator
    @Project.expose
    @commit
    def update(self, id):
        form = context.form

        # FIXME: This validation must be performed inside the validation
        # decorator
        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        if not len(form.keys()):
            raise HTTPStatus('708 No parameter exists in the form')

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

        if 'phase' in form and form['phase'] not in project_phases:
            raise HTTPStatus(
                f'706 Invalid phase, only one of '
                f'"{", ".join(project_phases)}" will be accepted'
            )

        if 'status' in form and form['status'] not in project_statuses:
            raise HTTPStatus(
                f'705 Invalid status, only one of '
                f'"{", ".join(project_statuses)}" will be accepted'
            )

        if 'title' in form and DBSession.query(Project) \
                .filter(Project.title == form['title']).count() >= 1:
            raise HTTPStatus(
                f'600 Another project with title: "{form["title"]}" is already'
                f' exists'
            )

        project.update_from_request()
        return project

