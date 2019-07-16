import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, given
from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.mule import MuleTask, worker
from sqlalchemy import and_

from dolphin.models import Issue, Project, Member, Workflow, Group, \
    Release, ReturnToTriageJob
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestRetuenTotriageJob(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(member)
        session.commit()

        workflow = Workflow(title='Default')
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

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1,
        )
        session.add(project)

        with Context(dict()):
            context.identity = member

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2,
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=2,
                room_id=3,
            )
            session.add(cls.issue2)
            session.flush()

            cls.job1 = ReturnToTriageJob(
                at=datetime.datetime.now(),
                issue_id=cls.issue2.id,
            )
            cls.job2 = ReturnToTriageJob(
                at=datetime.date.today() + datetime.timedelta(days=1),
                issue_id=cls.issue1.id,
            )

            session.add(cls.job1)
            session.add(cls.job2)
            session.commit()

    def test_schedule(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Schedule an issue',
            f'/apiv1/issues/id: {self.issue1.id}/jobs',
            'SCHEDULE',
            json=dict(at=datetime.datetime.now().isoformat())
        ):
            assert status == 200
            assert response.json['issueId'] == self.issue1.id

            session = self.create_session()
            assert session.query(ReturnToTriageJob) \
                .filter(and_(
                    ReturnToTriageJob.issue_id == self.issue1.id,
                    ReturnToTriageJob.status == 'new',
                )).count() == 1

            tasks = worker(
                tries=0,
                filters=MuleTask.type == 'return_to_triage_job',
            )
            assert len(tasks) == 2

            tasks = worker(
                tries=0,
                filters=MuleTask.type == 'return_to_triage_job',
            )
            assert len(tasks) == 0

            when(
                'Intended item with integer type not found',
                url_parameters=dict(id=0),
                json=given,
            )
            assert status == 404

            when(
                'Intended item with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

