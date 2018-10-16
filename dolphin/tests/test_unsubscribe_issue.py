from dolphin.models import Issue, Project, Member, Subscription
from dolphin.tests.helpers import LocalApplicationTestCase


class TestIssue(LocalApplicationTestCase):

    @classmethod
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
        session.flush()

        project = Project(
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1
        )
        session.add(issue1)
        session.flush()

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )
        session.add(issue2)
        session.flush()

        subscription1 = Subscription(
            subscribable=issue1.id,
            member=member.id
        )
        session.add(subscription1)

        subscription2 = Subscription(
            subscribable=issue2.id,
            member=member.id
        )
        session.add(subscription2)
        session.commit()

