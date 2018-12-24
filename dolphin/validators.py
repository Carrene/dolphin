import re

from nanohttp import validate, HTTPStatus, context
from restfulpy.orm import DBSession

from .models import *
from .models.organization import roles


TITLE_PATTERN = re.compile(r'^(?!\s).*[^\s]$')
DATETIME_PATTERN = re.compile(
    r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])' \
    r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$'
)
ORGANIZATION_TITLE_PATTERN = re.compile(
    r'^([0-9a-zA-Z]+-?[0-9a-zA-Z]*)*[\da-zA-Z]$'
)
USER_EMAIL_PATTERN = re.compile(
    r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
)


def release_exists_validator(releaseId, project, field):
    form = context.form
    try:
        releaseId = int(releaseId)
    except (TypeError, ValueError):
        raise HTTPStatus('750 Invalid Release Id Type')

    if 'releaseId' in form and not DBSession.query(Release) \
            .filter(Release.id == releaseId) \
            .one_or_none():
        raise HTTPStatus(
            f'607 Release not found with id: {context.form["releaseId"]}'
        )

    return releaseId


def release_status_value_validator(status, project, field):
    form = context.form
    if 'status' in form and form['status'] not in release_statuses:
        raise HTTPStatus(
            f'705 Invalid status value, only one of ' \
            f'"{", ".join(release_statuses)}" will be accepted'
        )
    return form['status']


def release_not_exists_validator(title, project, field):

    release = DBSession.query(Release).filter(Release.title == title) \
        .one_or_none()
    if release is not None:
        raise HTTPStatus(
            f'600 Another release with title: {title} is already exists.'
        )
    return title


def project_not_exists_validator(title, project, field):

    project = DBSession.query(Project).filter(Project.title == title) \
        .one_or_none()
    if project is not None:
        raise HTTPStatus(
            f'600 Another project with title: {title} is already exists.'
        )
    return title


def project_exists_validator(projectId, project, field):

    project = DBSession.query(Project) \
            .filter(Project.id == context.form['projectId']).one_or_none()
    if not project:
        raise HTTPStatus(
            f'601 Project not found with id: {context.form["projectId"]}'
        )
    return projectId


def project_status_value_validator(status, project, field):
    form = context.form
    if 'status' in form and form['status'] not in project_statuses:
        raise HTTPStatus(
            f'705 Invalid status value, only one of ' \
            f'"{", ".join(project_statuses)}" will be accepted'
        )
    return form['status']


def issue_not_exists_validator(title, project, field):
    form = context.form
    project = DBSession.query(Project) \
        .filter(Project.id == form['projectId']) \
        .one()

    for issue in project.issues:
        if issue.title == title:
            raise HTTPStatus(
                f'600 Another issue with title: "{title}" is already exists.'
            )

    return title


def kind_value_validator(kind, project, field):
    form = context.form
    if 'kind' in form and form['kind'] not in issue_kinds:
        raise HTTPStatus(
            f'717 Invalid kind, only one of ' \
            f'"{", ".join(issue_kinds)}" will be accepted'
        )
    return form['kind']


def issue_status_value_validator(status, project, field):
    form = context.form
    if 'status' in form and form['status'] not in issue_statuses:
        raise HTTPStatus(
            f'705 Invalid status, only one of ' \
            f'"{", ".join(issue_statuses)}" will be accepted'
        )
    return form['status']


def phase_exists_validator(phaseId, project, field):
    form = context.form

    try:
        phaseId = int(phaseId)
    except (TypeError, ValueError):
        raise HTTPStatus(f'613 Phase not found with id: {form["phaseId"]}')

    if 'phaseId' in form and not DBSession.query(Phase) \
            .filter(Phase.id == form['phaseId']) \
            .one_or_none():
        raise HTTPStatus(f'613 Phase not found with id: {form["phaseId"]}')

    return phaseId


def workflow_exists_validator(workflowId, project, field):

    try:
        workflowId = int(workflowId)
    except (TypeError, ValueError):
        raise HTTPStatus('743 Invalid Workflow Id Type')

    if not DBSession.query(Workflow) \
            .filter(Workflow.id == workflowId) \
            .one_or_none():
        raise HTTPStatus(f'616 Workflow not found with id: {workflowId}')

    return workflowId


def item_status_value_validator(status, project, field):
    form = context.form
    if 'status' in form and form['status'] not in item_statuses:
        raise HTTPStatus(
            f'705 Invalid status value, only one of ' \
            f'"{", ".join(item_statuses)}" will be accepted'
        )
    return form['status']


def member_exists_validator(memberId, project, field):
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


def resource_exists_validator(resourceId, project, field):
    form = context.form
    resource = DBSession.query(Resource) \
        .filter(Resource.id == form['resourceId']) \
        .one_or_none()
    if not resource:
        raise HTTPStatus(
            f'609 Resource not found with id: {form["resourceId"]}'
        )
    return resourceId


def organization_value_of_role_validator(role, container, field):
    if context.form.get('role') not in roles:
        raise HTTPStatus('756 Invalid Role Value')

    return role


release_validator = validate(
    title=dict(
        required='710 Title Not In Form',
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        pattern=(TITLE_PATTERN, '747 Invalid Title Format'),
        callback=release_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    cutoff=dict(
        pattern=(DATETIME_PATTERN, '702 Invalid Cutoff Format'),
        required='712 Cutoff Not In Form'
    ),
    status=dict(
        callback=release_status_value_validator
    )
)


update_release_validator = validate(
    title=dict(
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        pattern=(TITLE_PATTERN, '747 Invalid Title Format'),
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    cutoff=dict(
        pattern=(DATETIME_PATTERN, '702 Invalid Cutoff Format'),
    ),
    status=dict(
        callback=release_status_value_validator
    )
)


project_validator = validate(
    title=dict(
        required='710 Title Not In Form',
        callback=project_not_exists_validator,
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        pattern=(TITLE_PATTERN, '747 Invalid Title Format'),
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    status=dict(
        callback=project_status_value_validator
    ),
    workflowId=dict(
        callback=workflow_exists_validator
    ),
    releaseId=dict(
        callback=release_exists_validator
    ),
)


update_project_validator = validate(
    title=dict(
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        pattern=(TITLE_PATTERN, '747 Invalid Title Format'),
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    status=dict(
        callback=project_status_value_validator
    ),
)


issue_validator = validate(
    projectId=dict(
        required='713 Project Id Not In Form',
        type_=(int, '714 Invalid Project Id Type'),
        callback=project_exists_validator
    ),
    title=dict(
        required='710 Title Not In Form',
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        pattern=(TITLE_PATTERN, '747 Invalid Title Format'),
        callback=issue_not_exists_validator
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    dueDate=dict(
        pattern=(DATETIME_PATTERN, '701 Invalid Due Date Format'),
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
    phaseId=dict(
        callback=phase_exists_validator
    ),
    memberId=dict(
        callback=member_exists_validator
    )
)


update_issue_validator = validate(
    title=dict(
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        pattern=(TITLE_PATTERN, '747 Invalid Title Format'),
    ),
    description=dict(
        max_length=(512, '703 At Most 512 Characters Are Valid For Description')
    ),
    dueDate=dict(
        pattern=(DATETIME_PATTERN, '701 Invalid Due Date Format'),
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


assign_issue_validator = validate(
    memberId=dict(
        required='735 Member Id Not In Form',
        type_=(int, '736 Invalid Member Id Type'),
        callback=member_exists_validator
    ),
    phaseId=dict(
        required='737 Phase Id Not In Form',
        type_=(int, '738 Invalid Phase Id Type'),
        callback=phase_exists_validator
    )
)


organization_create_validator = validate(
    title=dict(
        required='710 Title Not In Form',
        max_length=(50,'704 At Most 50 Characters Are Valid For Title'),
        pattern=(ORGANIZATION_TITLE_PATTERN, '747 Invalid Title Format'),
    ),
)


organization_invite_validator = validate(
    email=dict(
        required='753 Email Not In Form',
        pattern=(USER_EMAIL_PATTERN, '754 Invalid Email Format')
    ),
    role=dict(
        required='755 Role Not In Form',
        callback=organization_value_of_role_validator,
    ),
    scopes=dict(
        required='765 Scopes Not In Form'
    ),
    applicationId=dict(
        required='764 Application Id Not In form'
    ),
    redirectUri=dict(
        required='766 Redirect Uri Not In form'
    ),
)


organization_join_validator = validate(
    token=dict(
        required='757 Token Not In Form',
    ),
)


token_obtain_validator = validate(
    organizationId=dict(
        required='761 Organization Id Not In Form',
        type_=(int, '763 Invalid Organization Id Type')
    ),
    authorizationCode=dict(
        required='762 Authorization Code Not In Form'
    ),
)


attachment_validator = validate(
    title=dict(
        max_length=(50, '704 At Most 50 Characters Are Valid For Title'),
        pattern=(TITLE_PATTERN, '747 Invalid Title Format'),
    ),
    attachment=dict(
        required='758 File Not In Form'
    )
)

