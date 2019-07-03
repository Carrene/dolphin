from datetime import datetime

from bddrest import status, response, when, given
from auditor.context import Context as AuditLogContext
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Member, Group, Workflow, Skill, Phase, Release, \
    Project, Issue, Item, Admin, IssuePhase, Dailyreport
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestListPhaseSummary(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.admin = Admin(
            title='First Admin',
            email='admin@example.com',
            access_token='access token 3',
            phone=111111111,
            reference_id=1
        )
        session.add(cls.admin)

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=987654321,
            reference_id=3
        )
        session.add(cls.member2)
        session.commit()

        workflow = Workflow(title='Default')
        session.add(workflow)

        skill = Skill(title='First Skill')
        cls.phase1 = Phase(
            title='backlog',
            order=5,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase1)

        cls.phase4 = Phase(
            title='Test',
            order=3,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase4)

        cls.phase3 = Phase(
            title='Development',
            order=2,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase3)

        cls.phase2 = Phase(
            title='Design',
            order=1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase2)

        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member2,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = cls.member1

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

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                due_date='2020-2-20',
                kind='feature',
                days=1,
                room_id=3
            )
            session.add(cls.issue2)
            session.flush()

            issue_phase1 = IssuePhase(
                issue_id=cls.issue1.id,
                phase_id=cls.phase1.id,
            )

            cls.item1 = Item(
                issue_phase=issue_phase1,
                member_id=cls.member1.id,
                start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
                estimated_hours=3,
            )
            session.add(cls.item1)

            dailyreport1 = Dailyreport(
                date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
                hours=1,
                note='note for dailyreport1',
                item=cls.item1,
            )
            session.add(dailyreport1)

            cls.item2 = Item(
                issue_phase=issue_phase1,
                member_id=cls.member2.id,
                start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
                estimated_hours=3,
            )
            session.add(cls.item2)

            issue_phase2 = IssuePhase(
                issue_id=cls.issue1.id,
                phase_id=cls.phase2.id,
            )

            cls.item3 = Item(
                issue_phase=issue_phase2,
                member_id=cls.member1.id,
                start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
                estimated_hours=3,
            )
            session.add(cls.item3)

            cls.item4 = Item(
                issue_phase=issue_phase2,
                member_id=cls.member2.id,
                start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
                estimated_hours=3,
            )
            session.add(cls.item4)

            issue_phase3 = IssuePhase(
                issue_id=cls.issue2.id,
                phase_id=cls.phase2.id,
            )

            cls.item5 = Item(
                issue_phase=issue_phase3,
                member_id=cls.member1.id,
            )
            session.add(cls.item5)
            session.commit()

    def test_list_phasesummary(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'List phases summaries',
            f'/apiv1/issues/issue_id: {self.issue1.id}/phasessummaries',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 4

            when('Sorting by phase id', query=dict(sort='id'))
            assert response.json[0]['id'] < response.json[1]['id']
            assert response.json[0]['status'] == 'in-progress'
            assert response.json[1]['status'] == None
            assert response.json[2]['status'] == None
            assert response.json[3]['status'] == 'to-do'

            when('Reverse sorting by phase id', query=dict(sort='-id'))
            assert response.json[1]['id'] < response.json[0]['id']

            when(
                'Filtering by the phase which member has worked on it',
                query=dict(id=self.phase2.id)
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.phase2.id
            assert response.json[0]['estimatedHours'] == \
                self.item3.estimated_hours + self.item4.estimated_hours

            when(
                'Filtering by the phase which member has not worked on it',
                query=dict(id=self.phase3.id)
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.phase3.id
            assert response.json[0]['estimatedHours'] == None

