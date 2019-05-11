import datetime

from bddrest import status, response, when
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Timecard, Workflow, Skill, Group, Release, \
    Project, Issue, Item, Phase
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestTimecard(LocalApplicationTestCase):

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

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

        phase = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
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

        issue = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue)
        session.flush()

        cls.item = Item(
            issue_id=issue.id,
            phase_id=phase.id,
            member_id=cls.member.id,
        )
        session.add(cls.item)

        cls.timecard = Timecard(
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            estimated_time=2,
            summary='Summary for timecard',
            item=cls.item,
        )
        session.add(cls.timecard)
        session.commit()

    def test_get(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Get a timecard',
            f'/apiv1/timecards/id: {self.timecard.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.timecard.id

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

