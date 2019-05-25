from datetime import datetime

from bddrest import status, response, when, given
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Group, Workflow, Skill, Phase, Release, \
    Project, Issue, Item
from dolphin.tests.helpers import LocalApplicationTestCase


class TestListGroup(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            phone=987654321,
            password='123ABCabc',
        )

        workflow = Workflow(title='Default')
        session.add(workflow)

        skill = Skill(title='First Skill')
        cls.phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase1)

        cls.phase2 = Phase(
            title='Triage',
            order=1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase2)

        cls.phase3 = Phase(
            title='Development',
            order=1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase3)

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
            manager=cls.member2,
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
            room_id=3
        )
        session.add(cls.issue2)

        cls.issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=4
        )
        session.add(cls.issue3)
        session.flush()

        cls.item1 = Item(
            issue_id=cls.issue1.id,
            phase_id=cls.phase1.id,
            member_id=cls.member1.id,
        )
        session.add(cls.item1)
        session.flush()

        cls.item2 = Item(
            issue_id=cls.issue2.id,
            phase_id=cls.phase3.id,
            member_id=cls.member1.id,
            start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(cls.item2)
        session.flush()

        cls.item3 = Item(
            issue_id=cls.issue3.id,
            phase_id=cls.phase2.id,
            member_id=cls.member1.id,
            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(cls.item3)
        session.commit()

    def test_list_item(self):
        self.login(self.member1.email)

        with self.given(
            'List item',
            '/apiv1/items',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when('Sort by id', query=dict(sort='id'))
            assert status == 200
            assert response.json[0]['id'] == self.item1.id
            assert response.json[1]['id'] == self.item2.id
            assert response.json[2]['id'] == self.item3.id

            when('Reverse sort by id', query=dict(sort='-id'))
            assert status == 200
            assert response.json[0]['id'] == self.item3.id
            assert response.json[1]['id'] == self.item2.id
            assert response.json[2]['id'] == self.item1.id

            when('Filter by id', query=dict(id=f'{self.item1.id}'))
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.item1.id

            when('Filter by id', query=dict(id=f'!{self.item1.id}'))
            assert len(response.json) == 2

            when(
                'Filter by `needEstimate` zone',
                query=dict(zone='needEstimate')
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.item1.id

            when(
                'Filter by `upcomingNuggets` zone',
                query=dict(zone='upcomingNuggets')
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.item2.id

            when(
                'Filter by `inProcessNuggets` zone',
                query=dict(zone='inProcessNuggets')
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.item3.id

            when(
                'Paginate item',
               query=dict(sort='id', take=1, skip=2)
            )
            assert response.json[0]['id'] == self.item3.id

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-id', take=1, skip=2)
            )
            assert response.json[0]['id'] == self.item1.id

            when('Request is not authorized', authorization=None)
            assert status == 401

