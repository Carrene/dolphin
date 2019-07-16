from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Project, Member, Workflow, Group, Release, Skill, \
    Phase, Issue, Item, IssuePhase
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestItem(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member1)
        session.commit()

        workflow = Workflow(title='Default')
        session.add(workflow)
        skill = Skill(title='First Skill')
        group = Group(title='default')

        cls.phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase1)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=group,
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = cls.member1

            cls.issue1 = Issue(
                project=cls.project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)

            issue_phase1 = IssuePhase(
                issue=cls.issue1,
                phase=cls.phase1,
            )

            cls.item = Item(
                issue_phase=issue_phase1,
                member=cls.member1,
            )
            session.add(cls.item)
            session.commit()

    def test_get(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'Getting a item',
            f'/apiv1/items/id: {self.item.id}',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == self.item.id
            assert response.json['perspective'] == 'overdue'
            assert response.json['status'] == 'to-do'
            assert 'issue' in response.json
            assert response.json['phaseId'] == self.phase1.id

            issue = response.json['issue']
            assert issue['title'] == self.issue1.title

            project = issue['project']
            assert project['title'] == self.project.title

            when(
                'Intended item with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended item with string type not found',
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

