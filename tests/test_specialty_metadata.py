from bddrest.authoring import status, response

from .helpers import LocalApplicationTestCase


class TestSpecialty(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/specialties',
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

            assert fields['title']['label'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

