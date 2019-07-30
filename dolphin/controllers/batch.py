from nanohttp import json
from restfulpy.controllers import RestController


class BatchController(RestController):

    @json
    def metadata(self):
        metadata = dict(
            name='Dailyreport', \
            primaryKeys=['id'], \
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
                    'type': None
                },
                projectId={
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
                    'name': 'projectId',
                    'key': 'projectId',
                    'primaryKey': True,
                    'label': 'Lori mepso',
                    'watermark': None,
                    'example': None,
                    'message': None,
                    'type': None
                }, \
                issueIds={
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
                    'name': 'issueIds',
                    'key': 'issueIds',
                    'primaryKey': True,
                    'label': 'Issue Ids',
                    'watermark': None,
                    'example': None,
                    'message': None,
                    'type': None
                },
            )
        )
        return metadata

