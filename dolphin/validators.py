import re

from nanohttp import validate, HTTPStatus, context
from restfulpy.orm import DBSession

from dolphin.models import Project, Release, Issue, issue_kinds, Member, \
    issue_statuses, item_statuses, project_statuses, release_statuses, \
    Resource, Phase


DATE_PATTERN = re.compile(
    r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])$'
)


def release_exists_validator(releaseId, container, field):
    form = context.form
    try:
        releaseId = int(releaseId)
    except (TypeError, ValueError):
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


def phase_exists_validator(phaseId, container, field):
    form = context.form

    if 'phaseId' in form and not DBSession.query(Phase) \
            .filter(Phase.id == form['phaseId']) \
            .one_or_none():
        raise HTTPStatus(f'613 Phase not found with id: {form["phaseId"]}')

    return phaseId


def item_status_value_validator(status, container, field):
    form = context.form
    if 'status' in form and form['status'] not in item_statuses:
        raise HTTPStatus(
            f'705 Invalid status value, only one of ' \
            f'"{", ".join(item_statuses)}" will be accepted'
        )
    return form['status']


def member_exists_validator(memberId, container, field):
    form = context.form
    try:
        memberId = int(memberId)
    except (TypeError, ValueError):
        raise HTTPStatus(
            f'610 Member not found with id: {context.form["memberId"]}'
        )

    if 'memberId' in form and not DBSession.query(Member) \
            .filter(Member.id == memberId) \
            .one_or_none():
        raise HTTPStatus(
            f'610 Member not found with id: {context.form["memberId"]}'
        )

    return memberId


def resource_exists_validator(resourceId, container, field):
    form = context.form
    resource = DBSession.query(Resource) \
        .filter(Resource.id == form['resourceId']) \
        .one_or_none()
    if not resource:
        raise HTTPStatus(
            f'609 Resource not found with id: {form["resourceId"]}'
        )
    return resourceId


release_validator = validate(
    title=dict(
        required='710 Title Not In Form',
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        callback=release_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid Cutoff Format'),
        required='712 Cutoff Not In Form'
    ),
    status=dict(
        callback=release_status_value_validator
    )
)


update_release_validator = validate(
    title=dict(
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid Cutoff Format'),
    ),
    status=dict(
        callback=release_status_value_validator
    )
)


project_validator = validate(
    title=dict(
        required='710 Title Not In Form',
        callback=project_not_exists_validator,
        max_length=(50, '704 At Most 50 Characters Are Valid For Title')
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
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
    memberId=dict(
        required='739 Member Id Not In Form',
        callback=member_exists_validator
    )
)


update_project_validator = validate(
    title=dict(
        max_length=(50, '704 At Most 50 Characters Are Valid For Title')
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    status=dict(
        callback=project_status_value_validator
    ),
    phase=dict(
        callback=project_phase_value_validator
    ),
    memberId=dict(
        callback=member_exists_validator
    )
)


issue_validator = validate(
    title=dict(
        required='710 Title Not In Form',
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        callback=issue_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid Due Date Format'),
        required='711 Due Date Not In Form'
    ),
    kind=dict(
        required='718 Kind Not In Form',
        callback=kind_value_validator
    ),
    status=dict(
        callback=issue_status_value_validator
    ),
    days=dict(
        type_=(int, '721 Invalid Days Type'),
        required='720 Days Not In Form'
    ),
    projectId=dict(
        required='713 Project Id Not In Form',
        type_=(int, '714 Invalid Project Id Type'),
        callback=project_exists_validator
    )
)


update_issue_validator = validate(
    title=dict(
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        callback=issue_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid Due Date Format'),
    ),
    kind=dict(
        callback=kind_value_validator
    ),
    status=dict(
        callback=issue_status_value_validator
    ),
    days=dict(
        type_=(int, '721 Invalid Days Type'),
    ),
)


update_item_validator = validate(
    status=dict(
        required='719 Status Not In Form',
        callback=item_status_value_validator
    )
)


subscribe_validator = validate(
    memberId=dict(
        required='735 Member Id Not In Form',
        type_=(int, '736 Invalid Member Id Type'),
        callback=member_exists_validator
    )
)


assign_issue_validator = validate(
    resourceId=dict(
        required='715 Resource Id Not In Form',
        type_=(int, '716 Invalid Resource Id Type'),
        callback=resource_exists_validator
    ),
    phaseId=dict(
        required='737 Phase Id Not In Form',
        type_=(int, '738 Invalid Phase Id Type'),
        callback=phase_exists_validator
    )
)

