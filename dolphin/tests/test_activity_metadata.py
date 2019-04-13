from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestActivity(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/activities',
            'METADATA'
        ):
            assert status == 200

            fields = response.json['fields']

            assert fields['item'] is not None
            assert fields['timeSpan'] is not None
            assert fields['description']['maxLength'] == 256
