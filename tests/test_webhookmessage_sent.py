from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, when, Remove, Update
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Issue, Project, Member, Workflow, Group, \
    Subscription, Release
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestSentMessegeWebhook(LocalApplicationTestCase):

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
            phone=123456788,
            reference_id=2
        )
        session.add(cls.member2)
        session.commit()

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

        with Context(dict()):
            context.identity = cls.member1

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
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

            cls.subscription_issue2 = Subscription(
                subscribable_id=cls.issue1.id,
                member_id=cls.member2.id,
                seen_at=datetime.utcnow()
            )
            session.add(cls.subscription_issue2)

            session.commit()
            session.expunge_all()

    def test_sent_messege_webhook(self):

        with oauth_mockup_server(), self.given(
            f'SENT message webhook handler',
            f'/apiv1/issues',
            f'SENT',
            query=dict(
                roomId=self.issue1.room_id,
                memberReferenceId=self.member1.reference_id,
            )
        ):
            assert status == 204

            session = self.create_session()
            session.add(self.subscription_issue1)
            session.expire(self.subscription_issue1)
            assert self.subscription_issue1.seen_at is not None

            session.add(self.subscription_issue2)
            session.expire(self.subscription_issue2)
            assert self.subscription_issue2.seen_at is None

            when(
                'roomId not in query',
                query=dict(a='a'),
            )
            assert status == 400

            when(
                'roomId must be integer',
                query=dict(roomId='a'),
            )
            assert status == 400

            when(
                'roomId must be integer',
                query=Update(roomId=0),
            )
            assert status == '605 Issue Not Found'

            when(
                'Member reference id not in query',
                query=Remove('memberReferenceId'),
            )
            assert status == 400

            when(
                'Member reference id must be integer',
                query=Update(memberReferenceId='not-integer'),
            )
            assert status == 400

            when(
                'Member not found',
                query=Update(memberReferenceId=0),
            )
            assert status == '611 User Not Found'

            # FIXME: Commented due to issue #519
            # self.logout()
            # when(
            #     'Trying with unauthorized',
            #     authorization=None
            # )
            # assert status == 401

