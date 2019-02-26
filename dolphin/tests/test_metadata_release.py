from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestRelease(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/releases',
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

            assert fields['description']['maxLength'] is not None
            assert fields['description']['minLength'] is not None
            assert fields['description']['label'] is not None
            assert fields['description']['watermark'] is not None
            assert fields['description']['name'] is not None
            assert fields['description']['notNone'] is not None
            assert fields['description']['required'] is not None

            assert fields['status']['label'] is not None
            assert fields['status']['watermark'] is not None
            assert fields['status']['name'] is not None
            assert fields['status']['required'] is not None

            assert fields['cutoff']['label'] is not None
            assert fields['cutoff']['watermark'] is not None
            assert fields['cutoff']['name'] is not None
            assert fields['cutoff']['notNone'] is not None
            assert fields['cutoff']['required'] is not None
            assert fields['cutoff']['pattern'] is not None
            assert fields['cutoff']['example'] is not None

            assert fields['dueDate']['label'] is not None
            assert fields['dueDate']['watermark'] is not None
            assert fields['dueDate']['name'] is not None
            assert fields['dueDate']['notNone'] is not None
            assert fields['dueDate']['required'] is not None
            assert fields['dueDate']['example'] is not None
            assert fields['dueDate']['readonly'] is not None

