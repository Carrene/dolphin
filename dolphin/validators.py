import re

from nanohttp import validate, HTTPStatus, context
from restfulpy.orm import DBSession

from dolphin.exceptions import empty_form_http_exception


DATE_PATTERN = re.compile(
    '^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])$'
)


release_validator = validate(
    title=dict(
        required=(True, '710 Title not in form'),
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=(True, '711 Due date not in form')
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid cutoff format'),
        required=(True, '712 Cutoff not in form')
    ),
)


update_release_validator = validate(
    title=dict(
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


project_validator = validate(
    title=dict(
        required=(True, '710 Title not in form'),
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=(True, '711 Due date not in form')
    ),
)


update_project_validator = validate(
    title=dict(
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
        required=(True, '713 Project id not in form'),
        type_=(int, '714 Invalid project id type')
    )
)


issue_validator = validate(
    title=dict(
        required=(True, '710 Title not in form'),
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        max_length=(512, '703 At most 512 characters are valid for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=(True, '711 Due date not in form')
    ),
    kind=dict(
        required=(True, '718 Kind not in form')
    ),
    days=dict(
        type_=(int, '721 Invalid days type'),
        required=(True, '720 Days not in form')
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
        required=(True, '719 Status not in form')
    )
)

