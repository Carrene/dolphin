from bddrest.authoring import status, response

from .helpers import LocalApplicationTestCase


class TestMember(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/organizations',
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

            assert fields['title']['pattern'] is not None
            assert fields['title']['patternDescription'] is not None
            assert fields['title']['required'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['minLength'] is not None
            assert fields['title']['maxLength'] is not None
            assert fields['title']['notNone'] is not None

            assert fields['url']['pattern'] is not None
            assert fields['url']['patternDescription'] is not None
            assert fields['url']['required'] is not None
            assert fields['url']['label'] is not None
            assert fields['url']['name'] is not None
            assert fields['url']['example'] is not None
            assert fields['url']['watermark'] is not None
            assert fields['url']['minLength'] is not None
            assert fields['url']['maxLength'] is not None
            assert fields['url']['notNone'] is not None

            assert fields['domain']['pattern'] is not None
            assert fields['domain']['patternDescription'] is not None
            assert fields['domain']['required'] is not None
            assert fields['domain']['label'] is not None
            assert fields['domain']['name'] is not None
            assert fields['domain']['example'] is not None
            assert fields['domain']['watermark'] is not None
            assert fields['domain']['minLength'] is not None
            assert fields['domain']['maxLength'] is not None
            assert fields['domain']['notNone'] is not None

            assert fields['logo']['protected'] is not None
            assert fields['logo']['notNone'] is not None
            assert fields['logo']['label'] is not None
            assert fields['logo']['required'] is not None

            assert fields['membersCount']['protected'] is not None
            assert fields['membersCount']['label'] is not None
            assert fields['membersCount']['required'] is not None
            assert fields['membersCount']['example'] is not None
            assert fields['membersCount']['type'] is not None
            assert fields['membersCount']['watermark'] is not None
            assert fields['membersCount']['readonly'] is not None
            assert fields['membersCount']['name'] is not None

            assert fields['role']['protected'] is not None
            assert fields['role']['label'] is not None
            assert fields['role']['required'] is not None
            assert fields['role']['example'] is not None
            assert fields['role']['watermark'] is not None
            assert fields['role']['type'] is not None
            assert fields['role']['name'] is not None

