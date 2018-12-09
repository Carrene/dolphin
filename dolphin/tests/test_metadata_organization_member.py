from bddrest.authoring import status, response
from dolphin.tests.helpers import LocalApplicationTestCase


 class TestMember(LocalApplicationTestCase):

     def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/organizationmembers',
            'METADATA'
        ):
            assert status == 200

             fields = response.json['fields']

            assert fields['email']['pattern'] is not None
            assert fields['email']['patternDescription'] is not None
            assert fields['email']['notNone'] is not None
            assert fields['email']['required'] is not None
            assert fields['email']['label'] is not None
            assert fields['email']['name'] is not None
            assert fields['email']['example'] is not None
            assert fields['email']['watermark'] is not None
            assert fields['email']['minLength'] is not None
            assert fields['email']['maxLength'] is not None

            assert fields['title']['pattern'] is not None
            assert fields['title']['patternDescription'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['minLength'] is not None
            assert fields['title']['maxLength'] is not None

            assert fields['password']['pattern'] is not None
            assert fields['password']['patternDescription'] is not None
            assert fields['password']['notNone'] is not None
            assert fields['password']['required'] is not None
            assert fields['password']['label'] is not None
            assert fields['password']['name'] is not None
            assert fields['password']['example'] is not None
            assert fields['password']['watermark'] is not None
            assert fields['password']['minLength'] is not None
            assert fields['password']['maxLength'] is not None

            assert fields['name']['pattern'] is not None
            assert fields['name']['patternDescription'] is not None
            assert fields['name']['required'] is not None
            assert fields['name']['label'] is not None
            assert fields['name']['name'] is not None
            assert fields['name']['example'] is not None
            assert fields['name']['watermark'] is not None
            assert fields['name']['minLength'] is not None
            assert fields['name']['maxLength'] is not None
            assert fields['name']['notNone'] is not None

            assert fields['phone']['pattern'] is not None
            assert fields['phone']['patternDescription'] is not None
            assert fields['phone']['required'] is not None
            assert fields['phone']['label'] is not None
            assert fields['phone']['name'] is not None
            assert fields['phone']['example'] is not None
            assert fields['phone']['watermark'] is not None
            assert fields['phone']['minLength'] is not None
            assert fields['phone']['maxLength'] is not None
            assert fields['phone']['notNone'] is not None

            assert fields['avatar']['protected'] is not None
            assert fields['avatar']['notNone'] is not None
            assert fields['avatar']['label'] is not None
            assert fields['avatar']['required'] is not None

