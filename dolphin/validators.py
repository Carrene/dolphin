import re

from nanohttp import validate, HTTPStatus, context
from restfulpy.orm import DBSession, commit

from dolphin.models import Project, Release
from dolphin.exceptions import empty_form_http_exception


DATE_PATTERN = re.compile(
    '^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])$'
)


def project_not_exists_validator(title, container, field):

    project = DBSession.query(Project).filter(Project.title == title) \
        .one_or_none()
    if project is not None:
        raise HTTPStatus(
            f'600 Another project with title: {title} is already exists.'
        )
    return title

def project_id_exists_validator(projectId, container, field):

    project = DBSession.query(Project) \
            .filter(Project.id == context.form['projectId']).one_or_none()
    if not project:
        raise HTTPStatus(f'601 Project not found with id: '
                         f'{context.form["projectId"]}'
        )
    return


def release_not_exists_validator(title, container, field):

    release = DBSession.query(Release).filter(Release.title == title) \
        .one_or_none()
    if release is not None:
        raise HTTPStatus(
            f'600 Another release with title: {title} is already exists.'
        )
    return title


release_validator = validate(
    title=dict(
        required=('710 Title not in form'),
        max_length=(50, '704 At most 50 characters are valid for title'),
        callback=release_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=('711 Due date not in form')
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid cutoff format'),
        required=('712 Cutoff not in form')
    ),
)


update_release_validator = validate(
    title=dict(
        max_length=(50, '704 At most 50 characters are valid for title'),
        callback=release_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid cutoff format'),
    ),
)


project_validator = validate(
    title=dict(
        required=('710 Title not in form'),
        callback=project_not_exists_validator,
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=('711 Due date not in form')
    ),
)


update_project_validator = validate(
    title=dict(
        callback=project_not_exists_validator,
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid cutoff format'),
    ),
)


assign_manager_validator = validate(
    projectId=dict(
#        required=('713 Project id not in form'),
        callback=project_id_exists_validator,
        type_=(int, '714 Invalid project id type')
    )
)


issue_validator = validate(
    title=dict(
        required=('710 Title not in form'),
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=('711 Due date not in form')
    ),
    kind=dict(
        required=('718 Kind not in form')
    ),
    days=dict(
        type_=(int, '721 Invalid days type'),
        required=('720 Days not in form')
    ),
)


update_issue_validator = validate(
    title=dict(
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
    ),
    days=dict(
        type_=(int, '721 Invalid days type'),
    ),
)


update_item_validator = validate(
    status=dict(
        required=('719 Status not in form')
    )
)

