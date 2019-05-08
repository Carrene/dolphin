from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestTimecard(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/timecards',
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

            assert fields['startDate']['label'] is not None
            assert fields['startDate']['watermark'] is not None
            assert fields['startDate']['pattern'] is not None
            assert fields['startDate']['example'] is not None
            assert fields['startDate']['name'] is not None
            assert fields['startDate']['notNone'] is not None
            assert fields['startDate']['required'] is not None

            assert fields['endDate']['label'] is not None
            assert fields['endDate']['watermark'] is not None
            assert fields['endDate']['pattern'] is not None
            assert fields['endDate']['example'] is not None
            assert fields['endDate']['name'] is not None
            assert fields['endDate']['notNone'] is not None
            assert fields['endDate']['required'] is not None

            assert fields['estimatedTime']['label'] is not None
            assert fields['estimatedTime']['watermark'] is not None
            assert fields['estimatedTime']['example'] is not None
            assert fields['estimatedTime']['name'] is not None
            assert fields['estimatedTime']['notNone'] is not None
            assert fields['estimatedTime']['required'] is not None

