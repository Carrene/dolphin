from auditor.context import Context as AuditLogContext
from bddrest import status, when, given

from dolphin.models import Issue, Project, Member, Workflow, Group, \
    Subscription, Release
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestMentionedMemberWebhook(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
        )
        session.add(cls.member1)

        workflow = Workflow(title='Default')
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
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

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
            days=2,
            room_id=3
        )
        session.add(cls.issue2)
        session.flush()

        subscription = Subscription(
            member_id=cls.member1.id,
            subscribable_id=cls.issue2.id,
            one_shot=True
        )
        session.add(subscription)
        session.commit()

    def test_mentioned_member_webhook(self):

        with oauth_mockup_server(), self.given(
            f'MENTIONED member webhook handler',
            f'/apiv1/issues',
            f'MENTIONED',
            query=dict(
                roomId=self.issue1.room_id,
                memberId=self.member1.reference_id,
            )
        ):
            assert status == 204

            session = self.create_session()
            one_shot_subscription = session.query(Subscription) \
                .filter(Subscription.subscribable_id == self.issue1.id) \
                .filter(Subscription.member_id == self.member1.id) \
                .filter(Subscription.one_shot.is_(True)) \
                .one()
            assert one_shot_subscription.seen_at is None

            when(
                'There is a subcription with one_shot',
                query=given | dict(roomId=self.issue2.room_id)
            )
            assert status == 204

            when(
                'roomId not in query',
                query=given - 'roomId',
            )
            assert status == 400

            when(
                'roomId must be integer',
                query=given | dict(roomId='not-integer'),
            )
            assert status == 400

            when(
                'Room not found',
                query=given | dict(roomId=0),
            )
            assert status == '605 Issue Not Found'

            when(
                'memberId not in query',
                query=given - 'memberId',
            )
            assert status == 400

            when(
                'memberId must be integer',
                query=given | dict(memberId='not-integer'),
            )
            assert status == 400

            when(
                'Member not found',
                query=given | dict(memberId=0),
            )
            assert status == '610 Member Not Found'

            # FIXME: Commented due to issue #519
            # self.logout()
            # when(
            #     'Trying with unauthorized',
            #     authorization=None
            # )
            # assert status == 401

