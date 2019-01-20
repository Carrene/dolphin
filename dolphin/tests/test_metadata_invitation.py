from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestProject(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/invitations',
            'METADATA'
        ):
            assert status == 200

            fields = response.json['fields']

            assert fields['role']['label'] is not None
            assert fields['role']['watermark'] is not None
            assert fields['role']['example'] is not None
            assert fields['role']['name'] is not None
            assert fields['role']['notNone'] is not None
            assert fields['role']['required'] is not None

            assert fields['expiredDate']['label'] is not None
            assert fields['expiredDate']['watermark'] is not None
            assert fields['expiredDate']['example'] is not None
            assert fields['expiredDate']['name'] is not None
            assert fields['expiredDate']['notNone'] is not None
            assert fields['expiredDate']['required'] is not None
            assert fields['expiredDate']['pattern'] is not None
            assert fields['expiredDate']['patternDescription'] is not None

            assert fields['email']['label'] is not None
            assert fields['email']['watermark'] is not None
            assert fields['email']['example'] is not None
            assert fields['email']['name'] is not None
            assert fields['email']['notNone'] is not None
            assert fields['email']['required'] is not None
            assert fields['email']['pattern'] is not None
            assert fields['email']['patternDescription'] is not None

            assert fields['organizationId']['label'] is not None
            assert fields['organizationId']['watermark'] is not None
            assert fields['organizationId']['example'] is not None
            assert fields['organizationId']['name'] is not None
            assert fields['organizationId']['notNone'] is not None
            assert fields['organizationId']['readonly'] is not None
            assert fields['organizationId']['required'] is not None

            assert fields['byMemberId']['label'] is not None
            assert fields['byMemberId']['watermark'] is not None
            assert fields['byMemberId']['example'] is not None
            assert fields['byMemberId']['name'] is not None
            assert fields['byMemberId']['readonly'] is not None
            assert fields['byMemberId']['notNone'] is not None
            assert fields['byMemberId']['required'] is not None

