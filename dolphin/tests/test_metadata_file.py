from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestFile(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/files',
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

            assert fields['caption']['maxLength'] is not None
            assert fields['caption']['minLength'] is not None
            assert fields['caption']['label'] is not None
            assert fields['caption']['watermark'] is not None
            assert fields['caption']['example'] is not None
            assert fields['caption']['name'] is not None
            assert fields['caption']['notNone'] is not None
            assert fields['caption']['required'] is not None

            assert fields['projectId']['label'] is not None
            assert fields['projectId']['watermark'] is not None
            assert fields['projectId']['example'] is not None
            assert fields['projectId']['name'] is not None
            assert fields['projectId']['notNone'] is not None
            assert fields['projectId']['required'] is not None

