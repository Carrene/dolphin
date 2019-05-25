from nanohttp import context
from nanohttp.contexts import Context
from bddrest import status, when, response
from auditor.context import Context as AuditLogContext

from dolphin.models import Issue, Project, Member, Workflow, Group, \
    Subscription, Release
from dolphin.tests.helpers import LocalApplicationTestCase


class TestSeeIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)

        workflow = Workflow(title='Default')
        group = Group(title='default')

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
        session.add(project)

        with Context(dict()):
            context.identity = cls.member

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
            session.flush()

            cls.subscription_issue1 = Subscription(
                subscribable_id=cls.issue1.id,
                member_id=cls.member.id,
            )
            session.add(cls.subscription_issue1)

            one_shot_subscription = Subscription(
                member_id=cls.member.id,
                subscribable_id=cls.issue1.id,
                one_shot=True,
            )
            session.add(one_shot_subscription)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                due_date='2016-2-20',
                kind='feature',
                days=2,
                room_id=3
            )
            session.add(cls.issue2)
            session.commit()
            session.expunge(cls.subscription_issue1)

    def test_see(self):
        self.login(self.member.email, self.member.password)

        with self.given(
            f'See a issues',
            f'/apiv1/issues/id: {self.issue1.id}',
            f'SEE',
        ):
            assert status == 200
            assert response.json['seenAt'] is not None

            session = self.create_session()
            session.add(self.subscription_issue1)
            session.expire(self.subscription_issue1)
            assert self.subscription_issue1.seen_at is not None

            when(
                'Issue is invalid',
                url_parameters=dict(id=0),
            )
            assert status == 404

            when(
                'Sending from',
                form=dict(whyDidYouDoThat='IDK'),
            )
            assert status == '709 Form Not Allowed'

            self.logout()
            when(
                'Trying with an unauthorized member',
                authorization=None
            )
            assert status == 401
