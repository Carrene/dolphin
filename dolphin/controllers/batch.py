from nanohttp import json
from restfulpy.controllers import RestController


class BatchController(RestController):

    @json
    def metadata(self):
        metadata = dict(
            name='Batch',
            primaryKeys=['id'],
            fields=dict(
                id={
                    'pattern': None,
                    'patternDescription': None,
                    'maxLength': None,
                    'minLength': None,
                    'minimum': 1,
                    'maximum': None,
                    'readonly': True,
                    'protected': None,
                    'notNone': True,
                    'required': False,
                    'default': None,
                    'name': 'id',
                    'key': 'id',
                    'primaryKey': True,
                    'label': 'ID',
                    'watermark': None,
                    'example': 1,
                    'message': None,
                    'type': None,
                },
                projectId={
                    'pattern': None,
                    'patternDescription': None,
                    'maxLength': None,
                    'minLength': None,
                    'minimum': None,
                    'maximum': None,
                    'readonly': True,
                    'protected': None,
                    'notNone': True,
                    'required': False,
                    'default': None,
                    'name': 'projectId',
                    'key': 'project_id',
                    'primaryKey': False,
                    'label': 'Lorem Ipsum',
                    'watermark': None,
                    'example': None,
                    'message': None,
                    'type': None,
                },
                issueIds={
                    'pattern': None,
                    'patternDescription': None,
                    'maxLength': None,
                    'minLength': None,
                    'minimum': None,
                    'maximum': None,
                    'readonly': True,
                    'protected': None,
                    'notNone': False,
                    'required': False,
                    'default': None,
                    'name': 'issueIds',
                    'key': 'issue_ids',
                    'primaryKey': False,
                    'label': 'Lorem Ipsum',
                    'watermark': None,
                    'example': None,
                    'message': None,
                    'type': None,
                },
            )
        )
        return metadata

