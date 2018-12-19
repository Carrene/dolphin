from bddrest.authoring import status, when, response

from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Phase, Workflow, Project, Issue


class TestSetPhase(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member)
        cls.triage = Phase(title='triage', order=0)
        backlog = Phase(title='backlog', order=-1)
        implement = Phase(title='implement', order=3)
        default_workflow = Workflow(
            title='default',
            phases=[cls.triage, backlog]
        )
        session.add(default_workflow)
        project = Project(
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        cls.issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)
        session.commit()

    def test_set_phase(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Set a phase for an issue',
            f'/apiv1/issues/issue_id:{self.issue1.id}/'
            f'phases/id:{self.triage.id}',
            'SET',
        ):
            assert status == 200
            assert 'issues' in response.json

