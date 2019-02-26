from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, when, given

from dolphin.models import Issue, Project, Member, Workflow, Group, \
    Subscription, Release
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=223456789,
            reference_id=2
        )
        session.add(cls.member2)

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
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
            member_id=cls.member1.id,
            seen_at=datetime.utcnow()
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

    def test_mention_issue(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            f'Mention a member in an issue as jaguar',
            f'/apiv1/issues',
            f'MENTION',
            json=dict(memberId=self.member1.id, roomId=self.issue1.room_id)
        ):
            assert status == 200

            session = self.create_session()
            session.add(self.subscription_issue1)
            session.expire(self.subscription_issue1)
            assert self.subscription_issue1.seen_at is None

            when(
                'Mention an unsubscribed member in an issue',
                json=dict(memberId=self.member2.id, roomId=self.issue1.room_id)
            )
            assert status == 200
            session = self.create_session()
            subscription_issue1_member2 = session.query(Subscription) \
                .filter(
                    Subscription.member_id == self.member2.id,
                    Subscription.subscribable_id == self.issue1.id,
                    Subscription.one_shot == True,
                ).one()
            assert subscription_issue1_member2.seen_at is None

            when(
                'memberId not found',
                json=given | dict(memberId=0),
            )
            assert status == '610 Member Not Found'

            when(
                'memberId not in form',
                json=given - 'memberId',
            )
            assert status == '735 Member Id Not In Form'

            when(
                'memberId type is invalid',
                json=given | dict(memberId='not-int'),
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'memberId is null',
                json=given | dict(memberId=None),
            )
            assert status == '774 Member Id Is Null'

            when(
                'roomId not found',
                json=given | dict(roomId=0),
            )
            assert status == '618 Chat Room Not Found'

            when(
                'roomId not in form',
                json=given - 'roomId',
            )
            assert status == '780 roomId Not In Form'

            when(
                'roomId type is invalid',
                json=given | dict(roomId='not-int'),
            )
            assert status == '781 Invalid roomId Type'

            when(
                'roomId is null',
                json=given | dict(roomId=None),
            )
            assert status == '779 roomId Is None'

            when(
                'Empty form',
                json={},
            )
            assert status == '708 Empty Form'

