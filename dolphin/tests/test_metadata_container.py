from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestContainer(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/containers',
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
            assert fields['title']['not_none'] is not None
            assert fields['title']['required'] is not None

            assert fields['description']['maxLength'] is not None
            assert fields['description']['minLength'] is not None
            assert fields['description']['label'] is not None
            assert fields['description']['watermark'] is not None
            assert fields['description']['name'] is not None
            assert fields['description']['not_none'] is not None
            assert fields['description']['required'] is not None

            assert fields['status']['label'] is not None
            assert fields['status']['watermark'] is not None
            assert fields['status']['name'] is not None
            assert fields['status']['not_none'] is not None
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
            assert fields['releaseId']['not_none'] is not None
            assert fields['releaseId']['watermark'] is not None

