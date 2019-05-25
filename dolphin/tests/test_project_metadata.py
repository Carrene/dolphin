from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestProject(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/projects',
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

            assert fields['status']['label'] is not None
            assert fields['status']['watermark'] is not None
            assert fields['status']['name'] is not None
            assert fields['status']['notNone'] is not None
            assert fields['status']['required'] is not None
            assert fields['status']['default'] is not None

            assert fields['boarding']['label'] is not None
            assert fields['boarding']['required'] is not None
            assert fields['boarding']['readonly'] is not None

            assert fields['dueDate']['label'] is not None
            assert fields['dueDate']['name'] is not None
            assert fields['dueDate']['type'] is not None
            assert fields['dueDate']['required'] is not None
            assert fields['dueDate']['readonly'] is not None

            assert fields['releaseId']['label'] is not None
            assert fields['releaseId']['name'] is not None
            assert fields['releaseId']['type'] is not None
            assert fields['releaseId']['required'] is not None
            assert fields['releaseId']['watermark'] is not None
            assert fields['releaseId']['notNone'] is not None
            assert fields['releaseId']['watermark'] is not None

            assert fields['managerId']['label'] is not None
            assert fields['managerId']['name'] is not None
            assert fields['managerId']['type'] is not None
            assert fields['managerId']['required'] is not None
            assert fields['managerId']['notNone'] is not None
            assert fields['managerId']['watermark'] is not None
            assert fields['managerId']['message'] is None
            assert fields['managerId']['readonly'] is not None

            assert fields['boardingValue']['label'] is not None
            assert fields['boardingValue']['name'] is not None
            assert fields['boardingValue']['required'] is not None
            assert fields['boardingValue']['readonly'] is not None

            assert fields['releaseCutoff']['label'] is not None
            assert fields['releaseCutoff']['name'] is not None
            assert fields['releaseCutoff']['required'] is not None
            assert fields['releaseCutoff']['readonly'] is not None

