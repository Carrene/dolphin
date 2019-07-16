from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Project, Member, Workflow, Issue, Subscription, \
    Group, Release, Phase, Skill, Item, IssuePhase
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestProject(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()
        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        cls.group1 = Group(title='First Group')
        cls.group2 = Group(title='Second Group')

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
            groups=[cls.group1],
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=222222222,
            reference_id=3
        )
        session.add(cls.member2)
        session.commit()

        cls.release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=cls.group1,
        )

        cls.release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=cls.group1,
        )

        cls.release3 = Release(
            title='My third release',
            description='A decription for my third release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=cls.group1,
        )

        cls.project1 = Project(
            release=cls.release1,
            workflow=workflow,
            group=cls.group1,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            status='active',
            room_id=1001
        )
        session.add(cls.project1)
        session.flush()

        cls.project2 = Project(
            release=cls.release2,
            workflow=workflow,
            group=cls.group1,
            manager=cls.member2,
            title='My second project',
            description='A decription for my project',
            status='active',
            room_id=1002
        )
        session.add(cls.project2)

        cls.project3 = Project(
            release=cls.release3,
            workflow=workflow,
            group=cls.group2,
            manager=cls.member2,
            title='My third project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000,
            status='on-hold',
        )
        session.add(cls.project3)

        cls.project4 = Project(
            release=cls.release3,
            workflow=workflow,
            group=cls.group2,
            manager=cls.member2,
            title='My third project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000,
            status='queued',
        )
        session.add(cls.project4)

        with Context(dict()):
            context.identity = cls.member1

            issue1 = Issue(
                project=cls.project1,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(issue1)

            issue2 = Issue(
                project=cls.project2,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=2,
                room_id=3,
            )
            session.add(issue2)

            issue3 = Issue(
                project=cls.project1,
                title='Third issue',
                description='This is description of third issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(issue3)

            subscription = Subscription(
                subscribable_id=cls.project1.id,
                member_id=cls.member1.id
            )
            session.add(subscription)

            phase1 = Phase(
                workflow=workflow,
                title='Backlog',
                order=1,
                skill=skill,
            )
            session.add(phase1)
            session.flush()

            phase2 = Phase(
                workflow=workflow,
                title='Test',
                order=2,
                skill=skill
            )
            session.add(phase1)
            session.flush()

            phase3 = Phase(
                workflow=workflow,
                title='Development',
                order=3,
                skill=skill
            )
            session.add(phase1)
            session.flush()

            issue_phase1 = IssuePhase(
                issue=issue1,
                phase=phase1,
            )
            session.add(issue_phase1)

            item1 = Item(
                member_id=cls.member1.id,
                issue_phase=issue_phase1,
            )
            session.add(item1)

            issue_phase2 = IssuePhase(
                issue=issue2,
                phase=phase2,
            )
            session.add(issue_phase2)

            item2 = Item(
                member_id=cls.member1.id,
                issue_phase=issue_phase2,
                start_date='2020-2-2',
                end_date='2020-2-3',
                estimated_hours=4,
            )
            session.add(item2)

            issue_phase3 = IssuePhase(
                issue=issue1,
                phase=phase2,
            )
            session.add(issue_phase3)

            item3 = Item(
                member_id=cls.member1.id,
                issue_phase=issue_phase2,
                start_date='2019-2-2',
                end_date='2019-2-3',
                estimated_hours=4,
            )
            session.add(item3)
            session.commit()

    def test_list(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'List projects',
            '/apiv1/projects',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 4

            when(
                'Sort projects by phases title',
                query=dict(sort='title')
            )
            assert status == 200
            assert response.json[0]['title'] == 'My first project'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'My third project'

            when(
                'Sorting project by statuses',
                query=dict(sort='status')
            )
            assert response.json[0]['status'] == 'active'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-status')
            )
            assert response.json[0]['status'] == 'queued'

            when(
                'Sorting project by due dates',
                query=dict(sort='dueDate')
            )
            assert response.json[0]['dueDate'] == '2020-02-03T00:00:00'
            assert response.json[1]['dueDate'] == None

            when(
                'Sorting project by due dates',
                query=dict(sort='-dueDate')
            )
            assert response.json[0]['dueDate'] == None
            assert response.json[1]['dueDate'] == None
            assert response.json[2]['dueDate'] == None
            assert response.json[3]['dueDate'] == '2020-02-03T00:00:00'

            when(
                'Sorting project by "isSubscribed" field',
                query=dict(sort='isSubscribed')
            )
            assert response.json[0]['isSubscribed'] == False

            when(
                'Revers sorting project by "isSubscribed" field',
                query=dict(sort='-isSubscribed')
            )
            assert response.json[0]['isSubscribed'] == True

            when(
                'Sorting projects by release title',
                query=dict(sort='releaseTitle')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['title'] == self.project1.title
            assert response.json[1]['title'] == self.project2.title
            assert response.json[2]['title'] == self.project3.title
            assert response.json[3]['title'] == self.project4.title

            when(
                'Reverse sorting projects by release title',
                query=dict(sort='-releaseTitle')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['title'] == self.project4.title
            assert response.json[1]['title'] == self.project3.title
            assert response.json[2]['title'] == self.project2.title
            assert response.json[3]['title'] == self.project1.title

            when(
                'Sorting projects by manager title',
                query=dict(sort='managerTitle')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['title'] == self.project1.title
            assert response.json[1]['title'] == self.project2.title
            assert response.json[2]['title'] == self.project3.title
            assert response.json[3]['title'] == self.project4.title

            when(
                'Reverse sorting projects by manager title',
                query=dict(sort='-managerTitle')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['title'] == self.project2.title
            assert response.json[1]['title'] == self.project4.title
            assert response.json[2]['title'] == self.project3.title
            assert response.json[3]['title'] == self.project1.title

            when(
                'Sorting projects by boarding title',
                query=dict(sort='boarding')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['title'] == self.project1.title
            assert response.json[1]['title'] == self.project2.title
            assert response.json[2]['title'] == self.project3.title
            assert response.json[3]['title'] == self.project4.title

            when(
                'Reverse sorting projects by boarding title',
                query=dict(sort='-boarding')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['title'] == self.project3.title
            assert response.json[1]['title'] == self.project1.title
            assert response.json[2]['title'] == self.project2.title
            assert response.json[3]['title'] == self.project4.title

            when(
                'Filtering projects',
                query=dict(sort='id', title='My first project')
            )
            assert response.json[0]['title'] == 'My first project'

            when(
                'Filtering by group ID',
                query=dict(groupId=f'IN({self.group2.id})')
            )
            assert len(response.json) == 2

            when(
                'List projects except one of them',
                query=dict(sort='id', title='!My awesome project')
            )
            assert response.json[0]['title'] == 'My first project'

            when(
                'List projects with filtering by status',
                query=dict(sort='id', status='active')
            )
            assert response.json[0]['status'] == 'active'

            when(
                'List projects with filtering by on-hold status to check '
                'their boarding is frozen',
                query=dict(sort='id', status='on-hold')
            )
            assert response.json[0]['status'] == 'on-hold'
            assert response.json[0]['boarding'] == 'on-time'

            when(
                'List projects excepts one of statuses',
                query=dict(sort='id', status='!active')
            )
            assert response.json[0]['status'] == 'on-hold'

            when(
                'Filtering project by boarding',
                query=dict(boarding='on-time')
            )
            assert status == 200
            assert len(response.json) == 3

            when(
                'Filter project by boarding using IN clause',
                query=dict(boarding='IN(on-time,frozen)')
            )
            assert status == 200
            assert len(response.json) == 3
            assert response.json[0]['title'] == self.project1.title
            assert response.json[1]['title'] == self.project2.title

            when(
                'Projects pagination',
                query=dict(sort='id', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'My third project'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == self.project2.title

            when('Request is not authorized', authorization=None)
            assert status == 401

