from contextlib import contextmanager

from nanohttp import RegexRouteController, json, settings, context
from bddrest import status, response, Update, when, Remove, Append, given
from restfulpy.mockup import mockup_http_server

from dolphin.models import Project, Manager, Release
from dolphin.tests.helpers import MockupApplication, LocalApplicationTestCase,\
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestProject(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        manager = Manager(
            title='First Manager',
            email='manager1@example.com',
            access_token='access token',
            phone=123456789
        )

        release = Release(
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        project = Project(
            manager=manager,
            release=release,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
            room_id=1000
        )

        hidden_project = Project(
            manager=manager,
            release=release,
            title='My hidden project',
            description='A decription for my project',
            due_date='2020-2-20',
            removed_at='2020-2-20',
            room_id=1000
        )

        session.add_all([manager, project, hidden_project, release])
        session.commit()
        cls.manager_id = manager.id
        cls.release = release

    def test_create(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Createing a project',
            '/apiv1/projects',
            'CREATE',
            form=dict(
                managerId=self.manager_id,
                title='My awesome project',
                description='A decription for my project',
                dueDate='2020-2-20',
                authorizationCode='authorization code'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome project'
            assert response.json['description'] == 'A decription for my project'
            assert response.json['dueDate'] == '2020-02-20T00:00:00'
            assert response.json['status'] == 'queued'

            when(
                'Manager id not in form',
                form=given - 'managerId' | dict(title='1')
            )
            assert status == '734 Manager Id Not In Form'

            when(
                'Manger not found with string type',
                form=given | dict(managerId='Alphabetical', title='1')
            )
            assert status == 608
            assert status.text.startswith('Manager not found')

            when(
                'Manager not found with integer type',
                form=given | dict(managerId=100, title='1')
            )
            assert status == 608
            assert status.text.startswith('Manager not found')

            when(
                'Release not found with string type',
                form=given | dict(releaseId='Alphabetical', title='1')
            )
            assert status == 607
            assert status.text.startswith('Release not found')

            when(
                'Release not found with integer type',
                form=given | dict(releaseId=100, title='1')
            )
            assert status == 607
            assert status.text.startswith('Release not found')

            when(
                'Title is not in form',
                form=Remove('title')
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For '\
                'Description'

            when(
                'Due date format is wrong',
                form=given | dict(
                    dueDate='20-20-20',
                    title='Another title'
                )
            )
            assert status == '701 Invalid Due Date Format'

            when(
                'Due date is not in form',
                form=given - ['dueDate'] | dict(title='Another title')
            )

            when(
                'Status value is invalid',
                form=given | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when('Request is not authorized', authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    form=given | dict(title='Another title')
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    form=given | dict(title='Another title')
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(title='Another title')
                )
                assert status == '801 Chat Server Internal Error'

    def test_update(self):
        self.login('manager1@example.com')

        with self.given(
            'Updating a project',
            '/apiv1/projects/id:2',
            'UPDATE',
            form=dict(
                title='My interesting project',
                description='A updated project description',
                dueDate='2200-2-20',
                status='active'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting project'
            assert response.json['description'] == 'A updated project ' \
                'description'
            assert response.json['dueDate'] == '2200-02-20T00:00:00'
            assert response.json['status'] == 'active'

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title is repetetive',
                form=Update(title='My awesome project')
            )
            assert status == 600
            assert status.text.startswith('Another project with title')

            when(
                'Title length is more than limit',
                form=Update(
                    title=((50 + 1) * 'a')
                )
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is more than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when(
                'Due date format is wrong',
                form=given | dict(
                    dueDate='2200-2-32',
                )
            )
            assert status == '701 Invalid Due Date Format'

            when(
                'Status value is invalid',
                form=given | dict(
                    status='progressing',
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when(
                'Invalid parameter is in the form',
                form=given + \
                    dict(invalid_param='External parameter')
            )
            assert status == 707
            assert status.text.startswith('Invalid field')

            when(
                'Request is not authorized',
                authorization=None
            )
            assert status == 401

        with self.given(
            'Updating project with empty form',
            '/apiv1/projects/id:2',
            'UPDATE',
            form=dict()
        ):
            assert status == '708 No Parameter Exists In The Form'

    def test_hide(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Hiding a project',
            '/apiv1/projects/id:2',
            'HIDE'
        ):
            session = self.create_session()
            project = session.query(Project) \
                .filter(Project.id == 2) \
                .one_or_none()
            assert status == 200
            project.assert_is_deleted()

            when(
                'Intended Project With String Type Not Found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when('Project not found', url_parameters=dict(id=100))
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_show(self):
        self.login('manager1@example.com')

        with self.given(
            'Showing a unhidden project',
            '/apiv1/projects/id:3',
            'SHOW'
        ):
            session = self.create_session()
            project = session.query(Project) \
                .filter(Project.id == 3) \
                .one_or_none()
            assert status == 200
            project.assert_is_not_deleted()

            when(
                'Project not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'There is parameter is form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_list(self):
        self.login('manager1@example.com')

        with self.given(
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
            assert response.json[0]['title'] == 'My awesome project'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'My interesting project'

        with self.given(
            'Filter projects',
            '/apiv1/projects',
            'LIST',
            query=dict(sort='id', title='My awesome project')
        ):
            assert response.json[0]['title'] == 'My awesome project'

            when(
                'List projects except one of them',
                query=dict(sort='id', title='!My awesome project')
            )
            assert response.json[0]['title'] == 'My interesting project'

        with self.given(
            'Project pagination',
            '/apiv1/projects',
            'LIST',
            query=dict(sort='id', take=1, skip=2)
        ):
            assert response.json[0]['title'] == 'My awesome project'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'My awesome project'

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_subscribe(self):
        self.login('manager1@example.com')

        with self.given(
            'Subscribe project',
            '/apiv1/projects/id:4',
            'SUBSCRIBE',
            form=dict(memberId=1)
        ):
            assert status == 200

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Intended project with integer type not found',
                url_parameters=dict(id=100),
            )
            assert status == 404

            when(
                'Member id not in form',
                form=given - 'memberId'
            )
            assert status == '735 Member Id Not In Form'

            when(
                'Member not found',
                form=given | dict(memberId=100)
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member id type is invalid',
                form=given | dict(memberId='Alphabetical')
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'Issue is already subscribed',
                url_parameters=dict(id=4),
                form=given | dict(memberId=1)
            )
            assert status == '611 Already Subscribed'

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_unsubscribe(self):
        self.login('manager1@example.com')

        with self.given(
            'Unsubscribe an project',
            '/apiv1/projects/id:4',
            'UNSUBSCRIBE',
            form=dict(memberId=1)
        ):
            assert status == 200

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Intended project with integer type not found',
                url_parameters=dict(id=100),
            )
            assert status == 404

            when(
                'Member id not in form',
                form=given - 'memberId'
            )
            assert status == '735 Member Id Not In Form'

            when(
                'Member not found',
                form=given | dict(memberId=100)
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member id type is invalid',
                form=given | dict(memberId='Alphabetical')
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'Issue is not subscribed yet',
                url_parameters=dict(id=4),
                form=given | dict(memberId=1)
            )
            assert status == '612 Not Subscribed Yet'

            when('Request is not authorized', authorization=None)
            assert status == 401

