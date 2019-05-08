from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestItem(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/items',
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

            assert fields['phaseId']['label'] is not None
            assert fields['phaseId']['name'] is not None
            assert fields['phaseId']['type'] is not None
            assert fields['phaseId']['required'] is not None
            assert fields['phaseId']['watermark'] is not None
            assert fields['phaseId']['notNone'] is not None
            assert fields['phaseId']['watermark'] is not None

            assert fields['issueId']['label'] is not None
            assert fields['issueId']['name'] is not None
            assert fields['issueId']['type'] is not None
            assert fields['issueId']['required'] is not None
            assert fields['issueId']['watermark'] is not None
            assert fields['issueId']['notNone'] is not None
            assert fields['issueId']['watermark'] is not None

            assert fields['memberId']['label'] is not None
            assert fields['memberId']['name'] is not None
            assert fields['memberId']['type'] is not None
            assert fields['memberId']['required'] is not None
            assert fields['memberId']['watermark'] is not None
            assert fields['memberId']['notNone'] is not None
            assert fields['memberId']['watermark'] is not None

