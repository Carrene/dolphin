from bddrest.authoring import status, response

from .helpers import LocalApplicationTestCase


class TestPhase(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/phasessummaries',
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

            assert fields['title']['name'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['required'] is not None

            assert fields['issueId']['label'] is not None
            assert fields['issueId']['name'] is not None
            assert fields['issueId']['type'] is not None
            assert fields['issueId']['required'] is not None
            assert fields['issueId']['watermark'] is not None
            assert fields['issueId']['notNone'] is not None
            assert fields['issueId']['watermark'] is not None

            assert fields['startDate']['label'] is not None
            assert fields['startDate']['name'] is not None
            assert fields['startDate']['type'] is not None
            assert fields['startDate']['required'] is not None

            assert fields['endDate']['label'] is not None
            assert fields['endDate']['name'] is not None
            assert fields['endDate']['type'] is not None
            assert fields['endDate']['required'] is not None

            assert fields['estimatedHours']['label'] is not None
            assert fields['estimatedHours']['name'] is not None
            assert fields['estimatedHours']['type'] is not None
            assert fields['estimatedHours']['required'] is not None
            assert fields['estimatedHours']['notNone'] is not None

            assert fields['hours']['label'] is not None
            assert fields['hours']['name'] is not None
            assert fields['hours']['type'] is not None
            assert fields['hours']['required'] is not None

            assert fields['status']['label'] is not None
            assert fields['status']['name'] is not None
            assert fields['status']['type'] is not None
            assert fields['status']['required'] is not None

