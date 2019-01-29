from bddrest import status, response, when

from dolphin.models import Member, Skill, Phase, Release, \
    Project, Issue, Item
from dolphin.tests.helpers import create_group, LocalApplicationTestCase, \
    oauth_mockup_server, create_workflow


from auditing.context import Context as AuditLogContext

class TestActivity(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )

        workflow = create_workflow()
        skill = Skill(title='First Skill')

        cls.phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase1)

        group = create_group()

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            member=cls.member,
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
            days=1,
            room_id=2
        )
        session.add(cls.issue2)
        session.flush()

        old_item = Item(
            issue_id=cls.issue2.id,
            phase_id=cls.phase1.id,
            member_id=cls.member.id,
        )
        session.add(old_item)

        cls.item = Item(
            issue_id=cls.issue1.id,
            phase_id=cls.phase1.id,
            member_id=cls.member.id,
        )
        session.add(cls.item)

        session.commit()

    def test_create(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Creating an activity',
            f'/apiv1/issues/id: {self.issue1.id}/activities',
            f'CREATE',
            json=dict(title=''),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['item']['id'] == self.item.id

