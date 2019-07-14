from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestIssue(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/issues',
            'METADATA'
        ):
            assert status == 200

            fields = response.json['fields']

            assert fields['id']['label'] is not None
            assert fields['id']['minimum'] is not None
            assert fields['id']['example'] is not None
            assert fields['id']['name'] is not None
            assert fields['id']['key'] is not None
            assert fields['id']['notNone'] is not None
            assert fields['id']['required'] is not None
            assert fields['id']['readonly'] is not None
            assert fields['id']['protected'] is not None
            assert fields['id']['primaryKey'] is not None

            assert fields['title']['maxLength'] is not None
            assert fields['title']['minLength'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['pattern'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

            assert fields['description']['maxLength'] is not None
            assert fields['description']['minLength'] is not None
            assert fields['description']['label'] is not None
            assert fields['description']['watermark'] is not None
            assert fields['description']['name'] is not None
            assert fields['description']['notNone'] is not None
            assert fields['description']['required'] is not None

            assert fields['stage']['label'] is not None
            assert fields['stage']['watermark'] is not None
            assert fields['stage']['name'] is not None
            assert fields['stage']['notNone'] is not None
            assert fields['stage']['required'] is not None
            assert fields['stage']['default'] is not None

            assert fields['dueDate']['label'] is not None
            assert fields['dueDate']['key'] is not None
            assert fields['dueDate']['name'] is not None
            assert fields['dueDate']['required'] is not None
            assert fields['dueDate']['readonly'] is not None

            assert fields['isDone']['label'] is not None
            assert fields['isDone']['name'] is not None
            assert fields['isDone']['required'] is not None
            assert fields['isDone']['readonly'] is not None

            assert fields['kind']['label'] is not None
            assert fields['kind']['watermark'] is not None
            assert fields['kind']['name'] is not None
            assert fields['kind']['notNone'] is not None
            assert fields['kind']['required'] is not None

            assert fields['days']['label'] is not None
            assert fields['days']['watermark'] is not None
            assert fields['days']['minimum'] is not None
            assert fields['days']['notNone'] is not None
            assert fields['days']['required'] is not None

            assert fields['boarding']['label'] is not None
            assert fields['boarding']['required'] is not None
            assert fields['boarding']['readonly'] is not None

            assert fields['priority']['label'] is not None
            assert fields['priority']['watermark'] is not None
            assert fields['priority']['name'] is not None
            assert fields['priority']['notNone'] is not None
            assert fields['priority']['required'] is not None
            assert fields['priority']['default'] is not None

            assert fields['phaseId']['label'] is not None
            assert fields['phaseId']['watermark'] is not None
            assert fields['phaseId']['name'] is not None
            assert fields['phaseId']['notNone'] is not None
            assert fields['phaseId']['required'] is not None
            assert fields['phaseId']['message'] is not None
            assert fields['phaseId']['readonly'] is not None
            assert fields['phaseId']['example'] is not None

            assert fields['tagId']['label'] is not None
            assert fields['tagId']['watermark'] is not None
            assert fields['tagId']['name'] is not None
            assert fields['tagId']['notNone'] is not None
            assert fields['tagId']['required'] is not None
            assert fields['tagId']['message'] is not None
            assert fields['tagId']['readonly'] is not None
            assert fields['tagId']['example'] is not None

            assert fields['seenAt']['label'] is not None
            assert fields['seenAt']['name'] is not None
            assert fields['seenAt']['required'] is not None
            assert fields['seenAt']['readonly'] is not None

            assert fields['relations']['label'] is not None
            assert fields['relations']['name'] is not None
            assert fields['relations']['required'] is not None
            assert fields['relations']['readonly'] is not None

            assert fields['boardingValue']['label'] is not None
            assert fields['boardingValue']['name'] is not None
            assert fields['boardingValue']['required'] is not None
            assert fields['boardingValue']['readonly'] is not None

            assert fields['unread']['label'] is not None
            assert fields['unread']['name'] is not None
            assert fields['unread']['required'] is not None
            assert fields['unread']['readonly'] is not None

            assert fields['origin']['label'] is not None
            assert fields['origin']['name'] is not None
            assert fields['origin']['notNone'] is not None
            assert fields['origin']['required'] is not None
            assert fields['origin']['readonly'] is not None
            assert fields['origin']['protected'] is not None
            assert fields['origin']['message'] is not None
            assert fields['origin']['example'] is not None
            assert fields['origin']['watermark'] is not None

            assert fields['createdByMemberId']['label'] is not None
            assert fields['createdByMemberId']['name'] is not None
            assert fields['createdByMemberId']['notNone'] is not None
            assert fields['createdByMemberId']['required'] is not None
            assert fields['createdByMemberId']['readonly'] is not None
            assert fields['createdByMemberId']['protected'] is not None
            assert fields['createdByMemberId']['message'] is not None
            assert fields['createdByMemberId']['example'] is not None
            assert fields['createdByMemberId']['watermark'] is not None

            assert fields['createdByReferenceId']['label'] is not None
            assert fields['createdByReferenceId']['name'] is not None
            assert fields['createdByReferenceId']['notNone'] is not None
            assert fields['createdByReferenceId']['required'] is not None
            assert fields['createdByReferenceId']['readonly'] is not None
            assert fields['createdByReferenceId']['protected'] is not None
            assert fields['createdByReferenceId']['message'] is not None
            assert fields['createdByReferenceId']['example'] is not None
            assert fields['createdByReferenceId']['watermark'] is not None

            assert fields['responseTime']['label'] is not None
            assert fields['responseTime']['name'] is not None
            assert fields['responseTime']['notNone'] is not None
            assert fields['responseTime']['required'] is not None
            assert fields['responseTime']['readonly'] is not None
            assert fields['responseTime']['protected'] is not None

            assert fields['lastMovingTime']['label'] is not None
            assert fields['lastMovingTime']['name'] is not None
            assert fields['lastMovingTime']['notNone'] is not None
            assert fields['lastMovingTime']['required'] is not None
            assert fields['lastMovingTime']['readonly'] is not None
            assert fields['lastMovingTime']['protected'] is not None

            assert fields['batchTitle']['label'] is not None
            assert fields['batchTitle']['name'] is not None
            assert fields['batchTitle']['required'] is not None
            assert fields['batchTitle']['readonly'] is not None

