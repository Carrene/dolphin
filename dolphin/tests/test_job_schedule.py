from auditor.context import Context as AuditLogContext
from bddrest import status, when, response
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Issue, Project, Member, Workflow, Group, Release, \
    Subscription
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestJob(LocalApplicationTestCase):

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
            room_id=1
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
                room_id=2
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=2,
                room_id=3
            )
            session.add(cls.issue2)

            cls.issue3 = Issue(
                project=project,
                title='Third issue',
                description='This is description of third issue',
                kind='feature',
                days=3,
                room_id=4
            )
            session.add(cls.issue2)

            session.flush()
            subscription1 = Subscription(
                member_id=member.id,
                subscribable_id=cls.issue2.id,
                one_shot=True,
            )
            session.add(subscription1)
            session.commit()

    def test_schedule(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Schedule an issue',
            f'/apiv1/issues/id: {self.issue1.id}/jobs',
            'SCHEDULE',
        ):
            assert status == 200
            assert response.json['id'] == self.issue1.id

