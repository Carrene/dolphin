from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, when, given, response
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Issue, Project, Member, Workflow, Group, Release, \
    Item, Phase, Skill, IssuePhase
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server


class TestItem(LocalApplicationTestCase):
    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member)
        session.commit()

        workflow = Workflow(title='Default')
        group = Group(title='default')

        skill = Skill(title='First Skill')
        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member,
            room_id=0,
            group=group,
        )

        project1 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project1)

        with Context(dict()):
            context.identity = cls.member

            cls.issue1 = Issue(
                project=project1,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)

            cls.phase1 = Phase(
                workflow=workflow,
                title='Development',
                order=3,
                skill=skill,
            )
            session.add(cls.phase1)
            session.flush()

            issue_phase1 = IssuePhase(
                issue_id=cls.issue1.id,
                phase_id=cls.phase1.id,
            )
            session.add(issue_phase1)
            session.flush()

            cls.item1 = Item(
                issue_phase_id=issue_phase1.id,
                member_id=cls.member.id,
                start_date=datetime.strptime('2019-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2019-2-3', '%Y-%m-%d'),
                estimated_hours=4,
                is_done=None,
            )
            session.add(cls.item1)
            session.commit()


    def test_update(self):
        self.login(self.member.email)

        form=dict(
            startDate=datetime.strptime('2019-2-2', '%Y-%m-%d'),
            endDate=datetime.strptime('2019-2-3', '%Y-%m-%d'),
            estimatedHours=4,
            isDone=None,
        )
        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Update a item',
            f'/apiv1/items/id:{self.item1.id}',
            'UPDATE',
            form=form,
        ):
            assert status == 200
            assert response.json['id'] == self.item1.id
            assert response.json['perspective'] == 'Due'
            assert 'issue' in response.json
            assert response.json['phaseId'] == self.phase1.id

            issue = response.json['issue']
            assert issue['title'] == self.issue1.title

            when(
                'Intended item with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given
            )
            assert status == 404

            when(
                'Chenged isDone',
                form=given | dict(isDone=True)
            )
            assert status == 200
            assert response.json['isDone'] == True

            when(
                'Intended item with integer type not found',
                url_parameters=dict(id=100),
                form=given
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

            when('Updating project with empty form', form=dict())
            assert status == '708 Empty Form'

