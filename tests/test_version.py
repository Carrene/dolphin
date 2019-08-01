from bddrest import status, response

from .helpers import LocalApplicationTestCase
from dolphin import __version__ as application_version


class TestVersion(LocalApplicationTestCase):

    def test_version(self):
        with self.given(
            'Retrieving application\'s version',
            '/apiv1/version'
        ):
            assert status == 200
            assert response.json['version'] == application_version

