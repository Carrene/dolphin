from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestItem(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/items',
            'METADATA'
        ):
            fields = response.json['fields']

            assert status == 200

            assert fields['status']['label'] is not None
            assert fields['status']['watermark'] is not None
            assert fields['status']['name'] is not None
            assert fields['status']['required'] is not None

            assert fields['end']['label'] is not None
            assert fields['end']['watermark'] is not None
            assert fields['end']['name'] is not None
            assert fields['end']['required'] is not None
            assert fields['end']['pattern'] is not None
            assert fields['end']['example'] is not None

