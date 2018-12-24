from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestPhase(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/phases',
            'METADATA'
        ):
            fields = response.json['fields']

            assert status == 200

            assert fields['title']['maxLength'] is not None
            assert fields['title']['minLength'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['pattern'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

            assert fields['order']['label'] is not None
            assert fields['order']['minimum'] is not None
            assert fields['order']['watermark'] is not None
            assert fields['order']['example'] is not None
            assert fields['order']['name'] is not None
            assert fields['order']['notNone'] is not None
            assert fields['order']['required'] is not None

