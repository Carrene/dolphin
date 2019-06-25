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

            assert fields['issuePhaseId']['label'] is not None
            assert fields['issuePhaseId']['name'] is not None
            assert fields['issuePhaseId']['type'] is not None
            assert fields['issuePhaseId']['required'] is not None
            assert fields['issuePhaseId']['watermark'] is not None
            assert fields['issuePhaseId']['notNone'] is not None
            assert fields['issuePhaseId']['watermark'] is not None

            assert fields['memberId']['label'] is not None
            assert fields['memberId']['name'] is not None
            assert fields['memberId']['type'] is not None
            assert fields['memberId']['required'] is not None
            assert fields['memberId']['watermark'] is not None
            assert fields['memberId']['notNone'] is not None
            assert fields['memberId']['watermark'] is not None

            assert fields['issue']['label'] is not None
            assert fields['issue']['name'] is not None
            assert fields['issue']['type'] is not None
            assert fields['issue']['required'] is not None
            assert fields['issue']['watermark'] is not None

            assert fields['isDone']['label'] is not None
            assert fields['isDone']['name'] is not None
            assert fields['isDone']['required'] is not None
            assert fields['isDone']['readonly'] is not None
            assert fields['isDone']['notNone'] is not None
            assert fields['isDone']['notNone'] is not None
            assert fields['isDone']['watermark'] is not None

            assert fields['perspective']['label'] is not None
            assert fields['perspective']['name'] is not None
            assert fields['perspective']['type'] is not None
            assert fields['perspective']['required'] is not None
            assert fields['perspective']['watermark'] is not None
            assert fields['perspective']['notNone'] is not None
            assert fields['perspective']['watermark'] is not None
            assert fields['perspective']['message'] is not None
            assert fields['perspective']['readonly'] is not None

