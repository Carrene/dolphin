from bddrest.authoring import status, response

from .helpers import LocalApplicationTestCase


class TestWorkflow(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/workflows',
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
            assert fields['title']['watermark'] is not None
            assert fields['title']['pattern'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

            assert fields['phases']['label'] is not None
            assert fields['phases']['watermark'] is not None
            assert fields['phases']['example'] is not None
            assert fields['phases']['name'] is not None
            assert fields['phases']['readonly'] is not None

