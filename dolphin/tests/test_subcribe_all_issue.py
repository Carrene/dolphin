from auditing.context import Context as AuditLogContext
from bddrest import status, when, response

from dolphin.models import Issue, Project, Member, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


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
            reference_id=1
        )

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(cls.project)

        cls.issue1 = Issue(
            project=cls.project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)

        issue2 = Issue(
            project=cls.project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2,
            room_id=3
        )
        session.add(issue2)
        session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Subscribe an issue',
            f'/apiv1/projects/{self.project.id}/issues',
            'SUBSCRIBE',
        ):
            assert status == 200


