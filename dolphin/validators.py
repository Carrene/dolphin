import re

from nanohttp import validate, HTTPStatus, context
from restfulpy.orm import DBSession, commit

from dolphin.models import Project, Release, Issue, issue_kinds, Member, \
    issue_statuses, item_statuses, project_statuses, release_statuses, Manager
from dolphin.exceptions import empty_form_http_exception


DATE_PATTERN = re.compile(
    '^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])$'
)


def release_exists_validator(releaseId, container, field):
    form = context.form
    try:
        releaseId = int(releaseId)
    except:
        raise HTTPStatus(
            f'607 Release not found with id: {context.form["releaseId"]}'
        )

    if 'releaseId' in form and not DBSession.query(Release) \
            .filter(Release.id == releaseId) \
            .one_or_none():
        raise HTTPStatus(
            f'607 Release not found with id: {context.form["releaseId"]}'
        )

    return releaseId


def release_status_value_validator(status, container, field):
    form = context.form
    if 'status' in form and form['status'] not in release_statuses:
        raise HTTPStatus(
            f'705 Invalid status value, only one of ' \
            f'"{", ".join(release_statuses)}" will be accepted'
        )
    return form['status']


def release_not_exists_validator(title, container, field):

    release = DBSession.query(Release).filter(Release.title == title) \
        .one_or_none()
    if release is not None:
        raise HTTPStatus(
            f'600 Another release with title: {title} is already exists.'
        )
    return title


def project_not_exists_validator(title, container, field):

    project = DBSession.query(Project).filter(Project.title == title) \
        .one_or_none()
    if project is not None:
        raise HTTPStatus(
            f'600 Another project with title: {title} is already exists.'
        )
    return title


def project_exists_validator(projectId, container, field):

    project = DBSession.query(Project) \
            .filter(Project.id == context.form['projectId']).one_or_none()
    if not project:
        raise HTTPStatus(
            f'601 Project not found with id: {context.form["projectId"]}'
        )
    return projectId


def project_status_value_validator(status, container, field):
    form = context.form
    if 'status' in form and form['status'] not in project_statuses:
        raise HTTPStatus(
            f'705 Invalid status value, only one of ' \
            f'"{", ".join(project_statuses)}" will be accepted'
        )
    return form['status']


def project_phase_value_validator(status, container, field):
    form = context.form
    if 'phase' in form and form['phase'] not in project_phases:
        raise HTTPStatus(
            f'706 Invalid phase value, only one of ' \
            f'"{", ".join(project_phases)}" will be accepted'
        )
    return form['phase']


def issue_not_exists_validator(title, container, field):

    issue = DBSession.query(Issue).filter(Issue.title == title) \
        .one_or_none()
    if issue is not None:
        raise HTTPStatus(
            f'600 Another issue with title: "{title}" is already exists.'
        )
    return title


def kind_value_validator(kind, container, field):
    form = context.form
    if 'kind' in form and form['kind'] not in issue_kinds:
        raise HTTPStatus(
            f'717 Invalid kind, only one of ' \
            f'"{", ".join(issue_kinds)}" will be accepted'
        )
    return form['kind']


def issue_status_value_validator(status, container, field):
    form = context.form
    if 'status' in form and form['status'] not in issue_statuses:
        raise HTTPStatus(
            f'705 Invalid status, only one of ' \
            f'"{", ".join(issue_statuses)}" will be accepted'
        )
    return form['status']


def item_status_value_validator(status, container, field):
    form = context.form
    if 'status' in form and form['status'] not in item_statuses:
        raise HTTPStatus(
            f'705 Invalid status value, only one of ' \
            f'"{", ".join(item_statuses)}" will be accepted'
        )
    return form['status']


def manager_exists_validator(managerId, container, field):
    form = context.form
    try:
        managerId = int(managerId)
    except:
        raise HTTPStatus(
            f'608 Manager not found with id: {context.form["managerId"]}'
        )

    if 'managerId' in form and not DBSession.query(Manager) \
            .filter(Manager.id == managerId) \
            .one_or_none():
        raise HTTPStatus(
            f'608 Manager not found with id: {context.form["managerId"]}'
        )

    return managerId


def member_exists_validator(memberId, container, field):
    form = context.form
    member = DBSession.query(Member) \
        .filter(Member.id == form['memberId']) \
        .one_or_none()
    if not member:
        raise HTTPStatus(f'610 Member not found with id: {form["memberId"]}')

    return memberId


release_validator = validate(
    title=dict(
        required='710 Title not in form',
        max_length=(50, '704 At most 50 characters are valid for title'),
        callback=release_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required='711 Due date not in form'
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid cutoff format'),
        required='712 Cutoff not in form'
    ),
    status=dict(
        callback=release_status_value_validator
    )
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
    status=dict(
        callback=release_status_value_validator
    )
)


project_validator = validate(
    title=dict(
        required='710 Title not in form',
        callback=project_not_exists_validator,
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required='711 Due date not in form'
    ),
    status=dict(
        callback=project_status_value_validator
    ),
    phase=dict(
        callback=project_phase_value_validator
    ),
    releaseId=dict(
        callback=release_exists_validator
    ),
    managerId=dict(
        required='734 Manager id not in form',
        callback=manager_exists_validator
    )
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
    status=dict(
        callback=project_status_value_validator
    ),
    phase=dict(
        callback=project_phase_value_validator
    )
)


assign_manager_validator = validate(
    projectId=dict(
        required='713 Project id not in form',
        type_=(int, '714 Invalid project id type'),
        callback=project_exists_validator
    )
)


issue_validator = validate(
    title=dict(
        required='710 Title not in form',
        max_length=(50, '704 At most 50 characters are valid for title'),
        callback=issue_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required='711 Due date not in form'
    ),
    kind=dict(
        required='718 Kind not in form',
        callback=kind_value_validator
    ),
    status=dict(
        callback=issue_status_value_validator
    ),
    days=dict(
        type_=(int, '721 Invalid days type'),
        required='720 Days not in form'
    ),
    projectId=dict(
        required='713 Project id not in form',
        type_=(int, '714 Invalid project id type'),
        callback=project_exists_validator
    )
)


update_issue_validator = validate(
    title=dict(
        max_length=(50, '704 At most 50 characters are valid for title'),
        callback=issue_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
    ),
    kind=dict(
        callback=kind_value_validator
    ),
    status=dict(
        callback=issue_status_value_validator
    ),
    days=dict(
        type_=(int, '721 Invalid days type'),
    ),
)


update_item_validator = validate(
    status=dict(
        required='719 Status not in form',
        callback=item_status_value_validator
    )
)


subscribe_issue_validator = validate(
    memberId=dict(
        required='735 Member id not in form',
        type_=(int, '736 Invalid member id type'),
        callback=member_exists_validator
    )
)

