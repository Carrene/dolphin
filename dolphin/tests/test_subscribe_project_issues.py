from auditing.context import Context as AuditLogContext
from bddrest import status, when, response

from dolphin.models import Issue, Project, Member, Workflow, Group, Release, \
    Subscription
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
        session.flush()

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

        subscription = Subscription(
            subscribable_id=cls.issue1.id,
            member_id=member.id
        )
        session.add(subscription)
        session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Subscribe all issues of a project',
            f'/apiv1/projects/id:{self.project.id}/issues',
            'SUBSCRIBE',
        ):
            assert status == 200
            assert response.json == {}

            when('Project is not found', url_parameters=dict(id=0))
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

