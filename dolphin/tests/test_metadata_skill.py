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

            assert fields['title']['label'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

