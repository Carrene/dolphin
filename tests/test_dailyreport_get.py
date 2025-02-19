from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, given
from nanohttp import context
from nanohttp.contexts import Context

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Dailyreport, Workflow, Specialty, Group, \
    Release, Project, Issue, Item, Phase, IssuePhase, Skill


class TestDailyreport(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
        )
        session.add(cls.member)
        session.commit()

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
        )
        group = Group(title='default')

        phase = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(phase)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = cls.member

            issue = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(issue)

            issue_phase1 = IssuePhase(
                issue=issue,
                phase=phase,
            )
            session.add(issue_phase1)

            cls.item = Item(
                issue_phase=issue_phase1,
                member=cls.member,
                start_date=datetime.now().date(),
                end_date=datetime.now().date(),
            )
            session.add(cls.item)

            cls.dailyreport = Dailyreport(
                date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
                hours=3,
                note='The note for a daily report',
                item=cls.item,
            )
            session.add(cls.dailyreport)
            session.commit()

    def test_get(self):
        self.login(self.member.email)
        session = self.create_session()

        with oauth_mockup_server(), self.given(
            f'Get a dailyreport',
            f'/apiv1/items/item_id: {self.item.id}/'
            f'dailyreports/id: {self.dailyreport.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.dailyreport.id

            when(
                'The item in not found',
                url_parameters=given | dict(item_id=0)
            )
            assert status == 404

            when(
                'Intended group with string type not found',
                url_parameters=given | dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group not found',
                url_parameters=given | dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

