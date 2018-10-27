from bddrest.authoring import status, response

from dolphin.tests.helpers import LocalApplicationTestCase


class TestMember(LocalApplicationTestCase):

    def test_metadata(self):
        with self.given(
            'Test metadata verb',
            '/apiv1/members',
            'METADATA'
        ):
            fields = response.json['fields']

            assert status == 200

            assert fields['title']['maxLength'] is not None
            assert fields['title']['minLength'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['not_none'] is not None
            assert fields['title']['required'] is not None

            assert fields['email']['label'] is not None
            assert fields['email']['watermark'] is not None
            assert fields['email']['name'] is not None
            assert fields['email']['not_none'] is not None
            assert fields['email']['required'] is not None
            assert fields['email']['pattern'] is not None
            assert fields['email']['example'] is not None

            assert fields['phone']['label'] is not None
            assert fields['phone']['watermark'] is not None
            assert fields['phone']['name'] is not None
            assert fields['phone']['required'] is not None

