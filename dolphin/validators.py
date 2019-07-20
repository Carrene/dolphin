import re

from nanohttp import validate, HTTPStatus, context, int_or_notfound, \
    HTTPBadRequest
from restfulpy.orm import DBSession
from restfulpy.datetimehelpers import parse_datetime

from .exceptions import *
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
WORKFLOW_TITLE_PATTERN = re.compile(r'^[^\s].+[^\s]$')


def release_exists_validator(releaseId, project, field):
    form = context.form
    try:
        releaseId = int(releaseId)
    except (TypeError, ValueError):
        raise StatusInvalidReleaseIdType()

    if 'releaseId' in form and not DBSession.query(Release) \
            .filter(Release.id == releaseId) \
            .one_or_none():
        raise StatusReleaseNotFound()

    return releaseId


def release_status_value_validator(status, project, field):
    form = context.form
    if 'status' in form and form['status'] not in release_statuses:
        raise StatusInvalidStatusValue(statuses_values=release_statuses)
    return form['status']


def release_not_exists_validator(title, project, field):

    release = DBSession.query(Release).filter(Release.title == title) \
        .one_or_none()
    if release is not None:
        raise StatusRepetitiveTitle()

    return title


def project_not_exists_validator(title, project, field):

    project = DBSession.query(Project).filter(Project.title == title) \
        .one_or_none()
    if project is not None:
        raise StatusRepetitiveTitle()

    return title


def project_accessible_validator(projectId, project, field):

    project = DBSession.query(Project) \
            .filter(Project.id == context.form['projectId']).one_or_none()
    if not project:
        raise StatusProjectNotFound()

    if project.is_deleted:
        raise StatusHiddenProjectIsNotEditable()

    return projectId


def event_repeat_value_validator(repeat, project, field):
    form = context.form
    if 'repeat' in form and form['repeat'] not in event_repeats:
        raise HTTPStatus(
            f'910 Invalid Repeat, only one of ' \
            f'"{", ".join(event_repeats)}" will be accepted'
        )

    return repeat


def project_status_value_validator(status, project, field):
    form = context.form
    if 'status' in form and form['status'] not in project_statuses:
        raise StatusInvalidStatusValue(statuses_values=project_statuses)
    return form['status']


def date_value_validator(date, project, field):
    try:
        date = parse_datetime(date)

    except ValueError:
        raise HTTPBadRequest()

    return date


def issue_not_exists_validator(title, project, field):
    form = context.form
    project = DBSession.query(Project) \
        .filter(Project.id == form['projectId']) \
        .one()

    for issue in project.issues:
        if issue.title == title:
            raise StatusRepetitiveTitle()


    return title

def relate_to_issue_exists_validator(relatedIssueId, container, field):
    if 'relatedIssueId' in context.form:
        related_issue_id = context.form.get('relatedIssueId')
        issue = DBSession.query(Issue).get(related_issue_id)

        if issue is None:
            raise StatusRelatedIssueNotFound(related_issue_id)

    return relatedIssueId


def kind_value_validator(kind, project, field):
    form = context.form
    if 'kind' in form and form['kind'] not in issue_kinds:
        raise StatusInvalidKind(issue_kinds)
    return form['kind']


def issue_stage_value_validator(stage, project, field):
    form = context.form
    if 'stage' in form and form['stage'] not in issue_stages:
        raise StatusInvalidStagesValue(stages_values=issue_stages)

    return form['stage']


def issue_priority_value_validator(priority, project, field):
    form = context.form
    if 'priority' in form and form['priority'] not in issue_priorities:
        raise StatusInvalidPriority(issue_priorities)
    return form['priority']


def phase_exists_validator(phaseId, project, field):
    form = context.form

    try:
        phaseId = int(phaseId)
    except (TypeError, ValueError):
        raise StatusPhaseNotFound()

    if 'phaseId' in form and not DBSession.query(Phase) \
            .filter(Phase.id == form['phaseId']) \
            .one_or_none():
        raise StatusPhaseNotFound()

    return phaseId


def workflow_exists_validator(workflowId, project, field):

    try:
        workflowId = int(workflowId)
    except (TypeError, ValueError):
        raise StatusInvalidWorkflowIdType()

    if not DBSession.query(Workflow) \
            .filter(Workflow.id == workflowId) \
            .one_or_none():
        raise StatusWorkflowNotFound()

    return workflowId


def item_status_value_validator(status, project, field):
    form = context.form
    if 'status' in form and form['status'] not in item_statuses:
        raise StatusInvalidStatusValue(statuses_values=item_statuses)

    return form['status']


def member_exists_validator(memberId, project, field):
    form = context.form
    try:
        memberId = int(memberId)

    except (TypeError, ValueError):
        raise StatusResourceNotFound(resource_id=context.form['memberId'])

    if 'memberId' in form and not DBSession.query(Member) \
            .filter(Member.id == memberId) \
            .one_or_none():
        raise StatusResourceNotFound(resource_id=context.form['memberId'])

    return memberId


def resource_exists_validator(resourceId, project, field):
    form = context.form
    resource = DBSession.query(Resource) \
        .filter(Resource.id == form['resourceId']) \
        .one_or_none()
    if not resource:
        raise StatusResourceNotFound(resource_id=context.form['resourceId'])
    return resourceId


def organization_value_of_role_validator(role, container, field):
    if context.form.get('role') not in roles:
        raise StatusInvalidRoleValue()

    return role


def group_exists_validator(title, project, field):

    group = DBSession.query(Group).filter(Group.title == title).one_or_none()
    if group is not None:
        raise StatusRepetitiveTitle()

    return title


def workflow_exists_validator_by_title(title, project, field):

    workflow = DBSession.query(Workflow) \
        .filter(Workflow.title == title) \
        .one_or_none()
    if workflow is not None:
        raise StatusRepetitiveTitle()

    return title


def tag_exists_validator(title, project, field):

    tag = DBSession.query(Tag) \
        .filter(
            Tag.title == title,
            Tag.organization_id == context.identity.payload['organizationId']
        ) \
        .one_or_none()
    if tag is not None:
        raise StatusRepetitiveTitle()

    return title


def specialty_exists_validator(title, project, field):
    specialty = DBSession.query(Specialty) \
        .filter(Specialty.title == title) \
        .one_or_none()
    if specialty is not None:
        raise StatusRepetitiveTitle()

    return title


def eventtype_exists_validator_by_title(title, project, field):
    event_type = DBSession.query(EventType) \
        .filter(EventType.title == title) \
        .one_or_none()
    if event_type is not None:
        raise StatusRepetitiveTitle()

    return title


def eventtype_exists_validator_by_id(event_type_id, project, field):
    event_type = DBSession.query(EventType).get(event_type_id)
    if event_type is None:
        raise StatusEventTypeNotFound()

    return event_type_id


def event_exists_validator(title, project, field):
    event = DBSession.query(Event) \
        .filter(Event.title == title) \
        .one_or_none()
    if event is not None:
        raise StatusRepetitiveTitle()

    return title


def item_exists_validator(item_id, container, field):
    int = int_or_notfound(item_id)

    item = DBSession.query(Item).filter(Item.id == item_id).one_or_none()
    if item is None:
        raise HTTPStatus('660 Item Not Found')

    return item_id


release_validator = validate(
    title=dict(
        required=StatusTitleNotInForm,
        max_length=(128, StatusMaxLenghtForTitle(128)),
        pattern=(TITLE_PATTERN, StatusInvalidTitleFormat),
        callback=release_not_exists_validator
    ),
    description=dict(
        max_length=(8192, StatusMaxLenghtForDescription(8192))
    ),
    cutoff=dict(
        pattern=(DATETIME_PATTERN, StatusInvalidCutoffFormat),
        required=StatusCutoffNotInForm
    ),
    status=dict(
        callback=release_status_value_validator
    ),
    managerId=dict(
        type_=(int, '608 Manager Not Found'),
        required='777 Manager Id Not In Form',
        not_none='778 Manager Id Is Null',
    ),
    launchDate=dict(
        pattern=(DATETIME_PATTERN, StatusInvalidLaunchDateFormat),
        required=StatusLaunchDateNotInForm
    ),
    groupId=dict(
        type_=(int, StatusInvalidGroupIdType),
        required=StatusGroupIdNotInForm,
        not_none=StatusGroupIdIsNull,
    ),
)


update_release_validator = validate(
    title=dict(
        max_length=(128, StatusMaxLenghtForTitle(128)),
        pattern=(TITLE_PATTERN, StatusInvalidTitleFormat),

    ),
    description=dict(
        max_length=(8192, StatusMaxLenghtForDescription(8192))
    ),
    cutoff=dict(
        pattern=(DATETIME_PATTERN, StatusInvalidCutoffFormat),
    ),
    status=dict(
        callback=release_status_value_validator
    ),
    managerId=dict(
        type_=(int, '608 Manager Not Found'),
        not_none='778 Manager Id Is Null',
    ),
    launchDate=dict(
        pattern=(DATETIME_PATTERN, StatusInvalidLaunchDateFormat),
    ),
    groupId=dict(
        type_=(int, StatusInvalidGroupIdType),
        not_none= StatusGroupIdIsNull,
    ),
)


project_validator = validate(
    title=dict(
        required=StatusTitleNotInForm,
        callback=project_not_exists_validator,
        max_length=(128, StatusMaxLenghtForTitle(128)),
        pattern=(TITLE_PATTERN, StatusInvalidTitleFormat),
    ),
    description=dict(
        max_length=(8192, StatusMaxLenghtForDescription(8192))
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
    managerId=dict(
        type_=(int, StatusManagerNotFound),
        required=StatusManagerIdNotInForm,
        not_none=StatusManagerIdIsNull,
    ),
    secondaryManagerId=dict(
        type_=(int, StatusSecondaryManagerNotFound),
    ),
)


update_project_validator = validate(
    title=dict(
        max_length=(128, StatusMaxLenghtForTitle(128)),
        pattern=(TITLE_PATTERN, StatusInvalidTitleFormat),
    ),
    description=dict(
        max_length=(8192, StatusMaxLenghtForDescription(8192))
    ),
    status=dict(
        callback=project_status_value_validator
    ),
    secondaryManagerId=dict(
        type_=(int, StatusSecondaryManagerNotFound),
    ),
    managerId=dict(
        type_=(int, StatusManagerNotFound),
        not_none=StatusManagerIdIsNull,
    ),
)


draft_issue_define_validator = validate(
    relatedIssueId=dict(
        type_=(int, StatusInvalidIssueIdType),
        callback=relate_to_issue_exists_validator,
    ),
)


draft_issue_finalize_validator = validate(
    priority=dict(
        required=StatusPriorityNotInForm,
        callback=issue_priority_value_validator
    ),
    projectId=dict(
        required=StatusProjectIdNotInForm,
        type_=(int, StatusInvalidProjectIdType),
        callback=project_accessible_validator,
    ),
    title=dict(
        required=StatusTitleNotInForm,
        max_length=(128, StatusMaxLenghtForTitle(128)),
        pattern=(TITLE_PATTERN, StatusInvalidTitleFormat),
        callback=issue_not_exists_validator
    ),
    description=dict(
        max_length=(8192, StatusMaxLenghtForDescription(8192))
    ),
    kind=dict(
        required=StatusKindNotInForm,
        callback=kind_value_validator
    ),
    stage=dict(
        callback=issue_stage_value_validator
    ),
    days=dict(
        type_=(int, StatusInvalidDaysType),
        required=StatusDaysNotInForm
    ),
    relatedIssueId=dict(
        type_=(int, StatusInvalidIssueIdType),
        not_none=StatusIssueIdIsNull,
        callback=relate_to_issue_exists_validator,
    ),
)


update_issue_validator = validate(
    title=dict(
        max_length=(128, StatusMaxLenghtForTitle(128)),
        pattern=(TITLE_PATTERN, StatusInvalidTitleFormat),
    ),
    description=dict(
        max_length=(8192, StatusMaxLenghtForDescription(8192))
    ),
    kind=dict(
        callback=kind_value_validator
    ),
    stage=dict(
        callback=issue_stage_value_validator
    ),
    days=dict(
        type_=(int, StatusInvalidDaysType),
    ),
    priority=dict(
        callback=issue_priority_value_validator,
    ),
)


update_item_validator = validate(
    status=dict(
        required=StatusStatusNotInForm,
        callback=item_status_value_validator
    )
)


assign_issue_validator = validate(
    memberId=dict(
        not_none=StatusResourceIdIsNull,
        type_=(int, StatusInvalidResourceIdType),
        callback=member_exists_validator
    ),
    phaseId=dict(
        required=StatusPhaseIdNotInForm,
        type_=(int, StatusInvalidPhaseIdType),
        callback=phase_exists_validator
    ),
    stage=dict(
        callback=issue_stage_value_validator
    ),
    description=dict(
        max_length=(
            512,
            '703 At Most 512 Characters Are Valid For Description'
        )
    )
)


unassign_issue_validator = validate(
    memberId=dict(
        not_none=StatusResourceIdIsNull,
        required=StatusResourceIdNotInForm,
        type_=(int, StatusInvalidResourceIdType),
        callback=member_exists_validator
    ),
    phaseId=dict(
        not_none=StatusPhaseIdIsNull,
        required=StatusPhaseIdNotInForm,
        type_=(int, StatusInvalidPhaseIdType),
        callback=phase_exists_validator
    )
)


organization_create_validator = validate(
    title=dict(
        required=StatusTitleNotInForm,
        max_length=(50, StatusMaxLenghtForTitle(50)),
        pattern=(ORGANIZATION_TITLE_PATTERN, StatusInvalidTitleFormat),
    ),
)


organization_invite_validator = validate(
    email=dict(
        required=StatusEmailNotInForm,
        pattern=(USER_EMAIL_PATTERN, StatusInvalidEmailFormat)
    ),
    role=dict(
        required=StatusRoleNotInForm,
        callback=organization_value_of_role_validator,
    ),
    scopes=dict(
        required=StatusScopesNotInForm
    ),
    applicationId=dict(
        required=StatusApplicationIdNotInForm
    ),
    redirectUri=dict(
        required=StatusRedirectUriNotInForm
    ),
)


organization_join_validator = validate(
    token=dict(
        required=StatusTokenNotInForm,
    ),
)


token_obtain_validator = validate(
    organizationId=dict(
        required=StatusOrganizationIdNotINForm,
        type_=(int, StatusInvalidOrganizationIdType)
    ),
    authorizationCode=dict(
        required=StatusAuthorizationCodeNotInForm,
    ),
)


issue_move_validator = validate(
    projectId=dict(
        required=StatusProjectIdNotInForm,
        type_=(int, StatusInvalidProjectIdType),
        callback=project_accessible_validator,
    ),
)


attachment_validator = validate(
    title=dict(
        max_length=(128, StatusMaxLenghtForTitle(128)),
        pattern=(TITLE_PATTERN, StatusInvalidTitleFormat),
    ),
    attachment=dict(
        required=StatusFileNotInForm
    )
)


group_create_validator = validate(
    description=dict(
        max_length=(
            8192, StatusMaxLenghtForDescription(8192)
        )
    ),
    title=dict(
        not_none=StatusTitleIsNull,
        required=StatusTitleNotInForm,
        max_length=(128, StatusMaxLenghtForTitle(128)),
        callback=group_exists_validator,
    )
)


group_update_validator = validate(
    description=dict(
        max_length=(
            8192, StatusMaxLenghtForDescription(8192)
        )
    ),
    title=dict(
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
    )
)


group_add_validator = validate(
    memberId=dict(
        not_none=StatusMemberIdIsNull,
        required=StatusMemberIdNotInForm,
        type_=(int , StatusInvalidMemberIdType),
    ),
)


group_remove_validator = validate(
    memberId=dict(
        not_none=StatusMemberIdIsNull,
        required=StatusMemberIdNotInForm,
        type_=(int , StatusInvalidMemberIdType),
    ),
)


workflow_create_validator = validate(
    description=dict(
        max_length=(
            8192, StatusMaxLenghtForDescription(8192)
        )
    ),
    title=dict(
        not_none=StatusTitleIsNull,
        required=StatusTitleNotInForm,
        max_length=(50, StatusMaxLenghtForTitle(50)),
        pattern=(WORKFLOW_TITLE_PATTERN, StatusInvalidTitleFormat),
        callback=workflow_exists_validator_by_title,
    )
)


tag_create_validator = validate(
    description=dict(
        max_length=(
            8192, StatusMaxLenghtForDescription(8192)
        )
    ),
    title=dict(
        not_none=StatusTitleIsNull,
        required=StatusTitleNotInForm,
        max_length=(50, StatusMaxLenghtForTitle(50)),
        callback=tag_exists_validator,
    )
)


tag_update_validator = validate(
    description=dict(
        max_length=(
            8192, StatusMaxLenghtForDescription(8192)
        )
    ),
    title=dict(
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
    )
)


issue_relate_validator = validate(
    targetIssueId=dict(
        not_none=StatusTargetIssueIdIsNull,
        required=StatusTargetIssueIdNotInForm,
        type_=(int, StatusInvalidTargetIssueIdType),
    )
)


issue_unrelate_validator = validate(
    targetIssueId=dict(
        not_none=StatusTargetIssueIdIsNull,
        required=StatusTargetIssueIdNotInForm,
        type_=(int, StatusInvalidTargetIssueIdType),
    )
)


draft_issue_relate_validator = validate(
    targetIssueId=dict(
        not_none=StatusTargetIssueIdIsNull,
        required=StatusTargetIssueIdNotInForm,
        type_=(int, StatusInvalidTargetIssueIdType),
    )
)


specialty_create_validator = validate(
    description=dict(
        max_length=(
            512, StatusMaxLenghtForDescription(512),
        ),
    ),
    title = dict(
        required=StatusTitleNotInForm,
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
        callback=specialty_exists_validator,
    ),
)


specialty_update_validator = validate(
    description=dict(
        max_length=(
            512, StatusMaxLenghtForDescription(512),
        ),
    ),
    title = dict(
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
    ),
)


workflow_update_validator = validate(
    description=dict(
        max_length=(
            8192, StatusMaxLenghtForDescription(8192)
        ),
    ),
    title = dict(
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
    ),
)


phase_update_validator = validate(
    specialtyId=dict(
        type_=(int, StatusInvalidSpecialtyIdType),
    ),
    order=dict(
        type_=(int, StatusInvalidOrderType),
    ),
    title=dict(
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
    ),
    description=dict(
        max_length=(
            512, StatusMaxLenghtForDescription(512),
        ),
    )
)


phase_validator = validate(
    title=dict(
        required=StatusTitleNotInForm,
        max_length=(50, StatusMaxLenghtForTitle(50)),
    ),
    order=dict(
        required=StatusOrderNotInForm,
        type_=(int, StatusInvalidOrderType),
    ),
    description=dict(
        max_length=(
            512, StatusMaxLenghtForDescription(512),
        ),
    )
)


eventtype_create_validator = validate(
   description=dict(
        max_length=(
            512, StatusMaxLenghtForDescription(512),
        ),
    ),
    title=dict(
        required=StatusTitleNotInForm,
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
        callback=eventtype_exists_validator_by_title
    ),
)


event_add_validator = validate(
    repeat=dict(
        required=StatusRepeatNotInForm,
        callback=event_repeat_value_validator,
    ),
    eventTypeId=dict(
        required=StatusTypeIdNotInForm,
        not_none=StatusEventTypeIdIsNull,
        callback=eventtype_exists_validator_by_id,
    ),
    startDate=dict(
        required=StatusStartDateNotInForm,
        pattern=(DATETIME_PATTERN, StatusInvalidStartDateFormat),
    ),
    endDate=dict(
        required=StatusEndDateNotInForm,
        pattern=(DATETIME_PATTERN, StatusInvalidEndDateFormat),
    ),
    title=dict(
        required=StatusTitleNotInForm,
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
        callback=event_exists_validator,
    ),
)


eventtype_update_validator = validate(
    description=dict(
        max_length=(
            512, StatusMaxLenghtForDescription(512),
        ),
    ),

    title=dict(
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50))
    ),
)


event_update_validator = validate(
    repeat=dict(
        callback=event_repeat_value_validator,
    ),
    eventTypeId=dict(
        not_none=StatusEventTypeIdIsNull,
        callback=eventtype_exists_validator_by_id,
    ),
    startDate=dict(
        pattern=(DATETIME_PATTERN, StatusInvalidStartDateFormat),
    ),
    endDate=dict(
        pattern=(DATETIME_PATTERN, StatusInvalidEndDateFormat),
    ),
    title=dict(
        not_none=StatusTitleIsNull,
        max_length=(50, StatusMaxLenghtForTitle(50)),
    ),
)


dailyreport_create_validator = validate(
    note=dict(
        required=StatusNoteNotInForm,
        max_length=(1024, StatusLimitedCharecterForNote),
    ),
    hours=dict(
        required=StatusHoursNotInForm,
        type_=(float, StatusInvalidHoursType),
        minimum=(0, StatusHoursMustBePositive)
    ),
    date=dict(
        required=StatusDateNotInForm,
        callback=date_value_validator,
    ),
)


dailyreport_update_validator = validate(
    note=dict(
        max_length=(1024, StatusLimitedCharecterForNote),
    ),
    hours=dict(
        type_=(float, StatusInvalidHoursType),
        minimum=(0, StatusHoursMustBePositive)
    ),
    date=dict(
        callback=date_value_validator,
    ),
)


search_member_validator = validate(
    query=dict(
        max_length=(50, '704 At Most 50 Characters Valid For Title'),
    )
)


search_issue_validator = validate(
    query=dict(
        max_length=(50, '704 At Most 50 Characters Valid For Title'),
    )
)


estimate_item_validator = validate(
    startDate=dict(
        required=StatusStartDateNotInForm,
        pattern=(DATETIME_PATTERN, StatusInvalidStartDateFormat),
        not_none=StatusStartDateIsNull,
    ),
    endDate=dict(
        required=StatusEndDateNotInForm,
        pattern=(DATETIME_PATTERN, StatusInvalidEndDateFormat),
        not_none=StatusEndDateIsNull,
    ),
    estimatedHours=dict(
        required=StatusEstimatedHoursNotInForm,
        type_=(int, StatusInvalidEstimatedHoursType),
        not_none=StatusEstimatedHoursIsNull,
    )
)

