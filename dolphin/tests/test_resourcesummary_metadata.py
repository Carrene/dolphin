from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestResourceSummary(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/resourcessummaries',
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
            assert fields['title']['example'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

            assert fields['load']['label'] is not None
            assert fields['load']['name'] is not None
            assert fields['load']['key'] is not None
            assert fields['load']['required'] is not None
            assert fields['load']['readonly'] is not None

            assert fields['startDate']['label'] is not None
            assert fields['startDate']['name'] is not None
            assert fields['startDate']['type'] is not None
            assert fields['startDate']['required'] is not None
            assert fields['startDate']['notNone'] is not None

            assert fields['endDate']['label'] is not None
            assert fields['endDate']['name'] is not None
            assert fields['endDate']['type'] is not None
            assert fields['endDate']['required'] is not None
            assert fields['endDate']['notNone'] is not None

            assert fields['estimatedHours']['label'] is not None
            assert fields['estimatedHours']['name'] is not None
            assert fields['estimatedHours']['type'] is not None
            assert fields['estimatedHours']['required'] is not None
            assert fields['estimatedHours']['notNone'] is not None

            assert fields['hoursWorked']['label'] is not None
            assert fields['hoursWorked']['name'] is not None
            assert fields['hoursWorked']['type'] is not None
            assert fields['hoursWorked']['required'] is not None

