from datetime import datetime

from bddrest import status, response, when, given
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Group, Workflow, Skill, Phase, Release, \
    Project, Issue, Item, Admin
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestListGroup(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.admin = Admin(
            title='First Admin',
            email='admin@example.com',
            access_token='access token 3',
            phone=111111111,
            reference_id=1
        )
        session.add(cls.admin)

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=987654321,
            reference_id=3
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

        cls.phase4 = Phase(
            title='Development',
            order=1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase4)

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
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)

        cls.issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            kind='feature',
            days=1,
            room_id=3
        )
        session.add(cls.issue2)

        cls.issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of third issue',
            kind='feature',
            days=1,
            room_id=4
        )
        session.add(cls.issue3)

        cls.issue4 = Issue(
            project=project,
            title='Fourth issue',
            description='This is description of fourth issue',
            kind='feature',
            days=1,
            room_id=5
        )
        session.add(cls.issue3)
        session.flush()

        cls.item1 = Item(
            issue_id=cls.issue1.id,
            phase_id=cls.phase1.id,
            member_id=cls.member1.id,
        )
        session.add(cls.item1)

        cls.item2 = Item(
            issue_id=cls.issue2.id,
            phase_id=cls.phase3.id,
            member_id=cls.member1.id,
            start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(cls.item2)

        cls.item3 = Item(
            issue_id=cls.issue3.id,
            phase_id=cls.phase2.id,
            member_id=cls.member1.id,
            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(cls.item3)

        cls.item4 = Item(
            issue_id=cls.issue4.id,
            phase_id=cls.phase4.id,
            member_id=cls.member2.id,
            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(cls.item4)

        cls.item5 = Item(
            issue_id=cls.issue4.id,
            phase_id=cls.phase2.id,
            member_id=cls.member1.id,
            status='done',
        )
        session.add(cls.item5)
        session.commit()

    def test_list_item(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'List item',
            '/apiv1/items',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 4

            when('Sort by id', query=dict(sort='id'))
            assert status == 200
            assert response.json[0]['id'] == self.item1.id
            assert response.json[1]['id'] == self.item2.id
            assert response.json[2]['id'] == self.item3.id

            when('Reverse sort by id', query=dict(sort='-id'))
            assert status == 200
            assert response.json[0]['id'] == self.item5.id
            assert response.json[1]['id'] == self.item3.id
            assert response.json[2]['id'] == self.item2.id

            when('Filter by id', query=dict(id=f'{self.item1.id}'))
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.item1.id

            when('Filter by id', query=dict(id=f'!{self.item1.id}'))
            assert len(response.json) == 3

            when(
                'The zone in query string is invalid',
                query=dict(zone='invalidZone')
            )
            assert status == 200
            assert response.json == []

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
                'Filter by `inProgressNuggets` zone',
                query=dict(zone='inProgressNuggets')
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.item3.id

            when(
                'Filter by `newlyAssigned` zone',
                query=dict(zone='newlyAssigned')
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.item5.id

            when(
                'Paginate item',
               query=dict(sort='id', take=1, skip=2)
            )
            assert response.json[0]['id'] == self.item3.id

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-id', take=1, skip=2)
            )
            assert response.json[0]['id'] == self.item2.id

            when('Request is not authorized', authorization=None)
            assert status == 401

        self.login(self.admin.email)
        with oauth_mockup_server(), self.given(
            'List items when request is from Admin',
            '/apiv1/items',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 5

