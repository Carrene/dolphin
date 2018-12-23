from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestTag(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/tags',
            'METADATA'
        ):
            assert status == 200

            fields = response.json['fields']

            assert fields['title']['maxLength'] is not None
            assert fields['title']['minLength'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

