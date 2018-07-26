
import re

from nanohttp import validate


DATE_PATTERN = re.compile(
    '^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])$'
)


release_validator = validate(
    title=dict(
        required=(True, '710 Title not exists'),
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        min_length=(20, '703 At least 20 characters are needed for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=(True, '711 Due date not exists')
    ),
    cutoff=dict(
        pattern=(DATE_PATTERN, '702 Invalid cutoff format'),
        required=(True, '712 Cutoff not exists')
    ),
)


project_validator = validate(
    title=dict(
        required=(True, '710 Title not exists'),
        max_length=(50, '704 At most 50 characters are valid for title')
    ),
    description=dict(
        min_length=(20, '703 At least 20 characters are needed for description')
    ),
    dueDate=dict(
        pattern=(DATE_PATTERN, '701 Invalid due date format'),
        required=(True, '711 Due date not exists')
    ),
)
