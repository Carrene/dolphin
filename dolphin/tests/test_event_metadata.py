from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestEvent(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/events',
            'METADATA'
        ):
            assert status == 200

            fields = response.json['fields']

            assert fields['id']['label'] is not None
            assert fields['id']['minimum'] is not None
            assert fields['id']['name'] is not None
            assert fields['id']['key'] is not None
            assert fields['id']['notNone'] is not None
            assert fields['id']['required'] is not None
            assert fields['id']['readonly'] is not None
            assert fields['id']['primaryKey'] is not None

            assert fields['title']['label'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None
            assert fields['title']['maxLength'] is not None
            assert fields['title']['readonly'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['message'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['type'] is not None

            assert fields['startDate']['label'] is not None
            assert fields['startDate']['notNone'] is not None
            assert fields['startDate']['required'] is not None
            assert fields['startDate']['readonly'] is not None
            assert fields['startDate']['watermark'] is not None
            assert fields['startDate']['example'] is not None
            assert fields['startDate']['message'] is not None
            assert fields['startDate']['notNone'] is not None
            assert fields['title']['type'] is not None

            assert fields['endDate']['label'] is not None
            assert fields['endDate']['notNone'] is not None
            assert fields['endDate']['required'] is not None
            assert fields['endDate']['readonly'] is not None
            assert fields['endDate']['watermark'] is not None
            assert fields['endDate']['example'] is not None
            assert fields['endDate']['message'] is not None
            assert fields['endDate']['notNone'] is not None

