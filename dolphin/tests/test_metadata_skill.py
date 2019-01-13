from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestSkill(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/skills',
            'METADATA'
        ):
            assert status == 200

            fields = response.json['fields']

            assert fields['phaseId']['label'] is not None
            assert fields['phaseId']['notNone'] is not None
            assert fields['phaseId']['required'] is not None

            assert fields['resourceId']['label'] is not None
            assert fields['resourceId']['notNone'] is not None
            assert fields['resourceId']['required'] is not None