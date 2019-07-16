from bddrest.authoring import status, response

from .helpers import LocalApplicationTestCase


class TestMember(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/members',
            'METADATA'
        ):
            fields = response.json['fields']

            assert status == 200

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
            assert fields['title']['name'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None

            assert fields['email']['label'] is not None
            assert fields['email']['name'] is not None
            assert fields['email']['notNone'] is not None
            assert fields['email']['required'] is not None
            assert fields['email']['pattern'] is not None
            assert fields['email']['example'] is not None

            assert fields['phone']['label'] is not None
            assert fields['phone']['name'] is not None
            assert fields['phone']['required'] is not None

            assert fields['organizationRole']['label'] is not None
            assert fields['organizationRole']['example'] is not None
            assert fields['organizationRole']['name'] is not None
            assert fields['organizationRole']['key'] is not None
            assert fields['organizationRole']['notNone'] is not None
            assert fields['organizationRole']['required'] is not None
            assert fields['organizationRole']['readonly'] is not None
            assert fields['organizationRole']['protected'] is not None
            assert fields['organizationRole']['primaryKey'] is not None

            assert fields['skills']['label'] is not None
            assert fields['skills']['example'] is not None
            assert fields['skills']['name'] is not None
            assert fields['skills']['key'] is not None
            assert fields['skills']['required'] is not None
            assert fields['skills']['readonly'] is not None
            assert fields['skills']['protected'] is not None

            assert fields['groups']['label'] is not None
            assert fields['groups']['example'] is not None
            assert fields['groups']['name'] is not None
            assert fields['groups']['key'] is not None
            assert fields['groups']['required'] is not None
            assert fields['groups']['readonly'] is not None
            assert fields['groups']['protected'] is not None

