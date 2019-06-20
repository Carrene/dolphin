from nanohttp import context
from nanohttp.contexts import Context
from auditor.context import Context as AuditLogContext
from bddrest import status, response, when

from dolphin.models import Issue, Member, Workflow, Group, Project, Release, \
    Skill, Phase, Item, IssuePhase
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
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

        workflow = Workflow(title='default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member,
            room_id=0,
            group=group,
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = member

            cls.issue = Issue(
                project=cls.project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue)

            cls.phase = Phase(
                workflow=workflow,
                title='Backlog',
                order=1,
                skill=skill,
            )
            session.add(cls.phase)
            session.flush()

            issue_phase1 = IssuePhase(
                issue=cls.issue,
                phase=cls.phase,
            )

            cls.item = Item(
                issue_phase=issue_phase1,
                member_id=member.id,
            )
            session.add(cls.item)
            session.commit()

    def test_get(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Getting a issue',
            f'/apiv1/issues/id:{self.issue.id}',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == self.issue.id
            assert response.json['title'] == self.issue.title
            assert response.json['project']['id'] == self.project.id
            assert response.json['stage'] == 'triage'
            assert response.json['isDone'] is None

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

