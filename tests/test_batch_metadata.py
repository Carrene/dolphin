from bddrest.authoring import status, response

from .helpers import LocalApplicationTestCase


class TestBatch(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/batches',
            'METADATA'
        ):
            assert status == 200

            fields = response.json['fields']

            assert fields['id']['primaryKey'] is not None
            assert fields['id']['readonly'] is not None
            assert fields['id']['notNone'] is not None
            assert fields['id']['required'] is not None
            assert fields['id']['label'] is not None
            assert fields['id']['minimum'] is not None
            assert fields['id']['example'] is not None
            assert fields['id']['watermark'] is not None
            assert fields['id']['message'] is not None

            assert fields['projectId']['key'] is not None
            assert fields['projectId']['notNone'] is not None
            assert fields['projectId']['readonly'] is not None
            assert fields['projectId']['label'] is not None
            assert fields['projectId']['watermark'] is not None
            assert fields['projectId']['name'] is not None
            assert fields['projectId']['example'] is not None
            assert fields['projectId']['message'] is not None

            assert fields['issueIds']['key'] is not None
            assert fields['issueIds']['notNone'] is not None
            assert fields['issueIds']['readonly'] is not None
            assert fields['issueIds']['label'] is not None
            assert fields['issueIds']['name'] is not None
            assert fields['issueIds']['watermark'] is not None
            assert fields['issueIds']['example'] is not None
            assert fields['issueIds']['name'] is not None

            assert fields['issueId']['key'] is not None
            assert fields['issueId']['notNone'] is not None
            assert fields['issueId']['readonly'] is not None
            assert fields['issueId']['label'] is not None
            assert fields['issueId']['name'] is not None
            assert fields['issueId']['watermark'] is not None
            assert fields['issueId']['example'] is not None
            assert fields['issueId']['name'] is not None

