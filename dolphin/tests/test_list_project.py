from bddrest import status, response, when

from dolphin.models import Project, Member, Workflow, Issue, Subscription
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestProject(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member1)

        workflow = Workflow(title='default')

        project1 = Project(
            workflow=workflow,
            member=member1,
            title='My first project',
            description='A decription for my project',
            status='active',
            room_id=1001
        )
        session.add(project1)
        session.flush()

        project2 = Project(
            workflow=workflow,
            member=member1,
            title='My second project',
            description='A decription for my project',
            status='on-hold',
            room_id=1002
        )
        session.add(project2)

        project3 = Project(
            workflow=workflow,
            member=member1,
            title='My third project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(project3)

        issue1 = Issue(
            project=project1,
            title='First issue',
            description='This is description of first issue',
            due_date='2030-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)

        issue2 = Issue(
            project=project2,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2,
            room_id=3
        )
        session.add(issue2)

        subscription = Subscription(
            subscribable=project1.id,
            member=member1.id
        )
        session.add(subscription)
        session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List projects',
            '/apiv1/projects',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            with self.given(
                'Sort projects by phases title',
                '/apiv1/projects',
                'LIST',
                query=dict(sort='title')
            ):
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
                assert response.json[0]['dueDate'] == '2020-02-20T00:00:00'
                assert response.json[1]['dueDate'] == '2030-02-20T00:00:00'

                when(
                    'Sorting project by due dates',
                    query=dict(sort='!dueDate')
                )
                assert response.json[0]['dueDate'] == '2030-02-20T00:00:00'
                assert response.json[1]['dueDate'] == '2020-02-20T00:00:00'

                when(
                    'Sorting project by "isSubscribed" field',
                    query=dict(sort='isSubscribed')
                )
                assert response.json[0]['isSubscribed'] == False

                when(
                    'Revers sorting project by "isSubscribed" field',
                    query=dict(sort='!isSubscribed')
                )
                assert response.json[0]['isSubscribed'] == True

            with self.given(
                'Filter projects',
                '/apiv1/projects',
                'LIST',
                query=dict(sort='id', title='My first project')
            ):
                assert response.json[0]['title'] == 'My first project'

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
                    'List projects excepts one of statuses',
                    query=dict(sort='id', status='!active')
                )
                assert response.json[0]['status'] == 'on-hold'

            with self.given(
                'Project pagination',
                '/apiv1/projects',
                'LIST',
                query=dict(sort='id', take=1, skip=2)
            ):
                assert response.json[0]['title'] == 'My third project'

                when(
                    'Manipulate sorting and pagination',
                    query=dict(sort='-title', take=1, skip=2)
                )
                assert response.json[0]['title'] == 'My first project'

                when('Request is not authorized', authorization=None)
                assert status == 401

