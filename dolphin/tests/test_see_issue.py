from auditing.context import Context as AuditLogContext
from bddrest import status, when

from dolphin.models import Issue, Project, Member, Workflow, Group, \
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
        session.add(member)

        workflow = Workflow(title='Default')
        group = Group(title='default')

        project = Project(
            workflow=workflow,
            group=group,
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

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
            member_id=member.id,
        )
        session.add(cls.subscription_issue1)

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

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            f'See a subscribed issues',
            f'/apiv1/issues/id: {self.issue1.id}',
            f'SEE',
        ):
            assert status == 200

            session = self.create_session()
            session.add(self.subscription_issue1)
            session.expire(self.subscription_issue1)
            assert self.subscription_issue1.seen_at is not None

            when(
                'See an unsubscribed issue',
                url_parameters=dict(id=self.issue2.id),
            )
            assert status == '637 Not Subscribed Issue'

            when(
                'Issue is invalid',
                url_parameters=dict(id=0),
            )
            assert status == 404

            when(
                'Sending from',
                form=dict(whyDidYouDoThat='IDK'),
            )
            assert status == 709

            self.logout()
            when(
                'Trying with an unauthorized member',
                authorization=None
            )
            assert status == 401
