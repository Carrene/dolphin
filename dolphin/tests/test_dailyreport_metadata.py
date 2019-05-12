from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestDailyreport(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/dailyreports',
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

            assert fields['date']['label'] is not None
            assert fields['date']['watermark'] is not None
            assert fields['date']['pattern'] is not None
            assert fields['date']['example'] is not None
            assert fields['date']['name'] is not None
            assert fields['date']['notNone'] is not None
            assert fields['date']['required'] is not None

            assert fields['hours']['label'] is not None
            assert fields['hours']['watermark'] is not None
            assert fields['hours']['example'] is not None
            assert fields['hours']['name'] is not None
            assert fields['hours']['notNone'] is not None
            assert fields['hours']['required'] is not None

            assert fields['itemId']['label'] is not None
            assert fields['itemId']['watermark'] is not None
            assert fields['itemId']['example'] is not None
            assert fields['itemId']['name'] is not None
            assert fields['itemId']['notNone'] is not None
            assert fields['itemId']['required'] is not None

