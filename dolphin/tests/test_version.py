from bddrest import status, response

from dolphin import __version__ as application_version
from dolphin.tests.helpers import LocalApplicationTestCase


class TestVersion(LocalApplicationTestCase):

    def test_version(self):
        with self.given(
            'Retrieving application\'s version',
            '/apiv1/version'
        ):
            assert status == 200
            assert response.json['version'] == application_version
