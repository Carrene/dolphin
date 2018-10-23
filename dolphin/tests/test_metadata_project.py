from bddrest import status, response, when

from dolphin.models import Project, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestProject(LocalApplicationTestCase):

    def test_list(self):
        with self.given(
            'Listmadfdsf projects',
            '/apiv1/projects',
            'METADATA',
        ):
            fields = response.json['fields']

            assert status == 200
