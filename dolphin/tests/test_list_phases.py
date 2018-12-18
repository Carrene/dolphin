from bddrest.authoring import status, response

from dolphin.models import Phase, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestListPhase(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        cls.session = cls.create_session()
        triage = Phase(title='triage', order=0)
        design = Phase(title='design', order=2)
        implement = Phase(title='implement', order=3)
        default_workflow = Workflow(
            title='default',
            phases=[triage,design]
        )
        cls.session.add(default_workflow)
        cls.session.commit()

    def test_list_phases(self):
        with oauth_mockup_server(), self.given(
            'List phases of a workflow',
            '/apiv1/workflows/id:1/phases',
            'LIST',
        ):
            from pudb import set_trace; set_trace()
            assert status == 200

