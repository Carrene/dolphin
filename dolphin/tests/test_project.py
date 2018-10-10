from bddrest import status, response, Update, when, Remove, given

from dolphin.models import Project, Manager, Release
from dolphin.tests.helpers import MockupApplication, LocalApplicationTestCase,\
    oauth_mockup_server, chat_mockup_server, chat_server_status, \
    room_mockup_server


class TestProject(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        manager1 = Manager(
            title='First Manager',
            email='manager1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(manager1)

        manager2 = Manager(
            title='Second Manager',
            email='manager2@example.com',
            access_token='access token 2',
            phone=123457689,
            reference_id=3
        )
        session.add(manager2)

        manager3 = Manager(
            title='Third Manager',
            email='manager3@example.com',
            access_token='access token 3',
            phone=123467859,
            reference_id=4
        )
        session.add(manager3)

        manager4 = Manager(
            title='Fourth Manager',
            email='manager4@example.com',
            access_token='access token 4',
            phone=142573689,
            reference_id=5
        )
        session.add(manager4)

        release = Release(
            title='My first release',
            description='A decription for my release',
            cutoff='2030-2-20',
        )
        session.add(release)

        project1 = Project(
            manager=manager1,
            release=release,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)

        project2 = Project(
            manager=manager1,
            release=release,
            title='My second project',
            description='A decription for my project',
            room_id=1002
        )
        session.add(project2)

        hidden_project = Project(
            manager=manager1,
            release=release,
            title='My hidden project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(hidden_project)
        session.commit()
        cls.manager_id = manager1.id
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
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome project'
            assert response.json['description'] == 'A decription for my project'
            assert response.json['status'] == 'queued'
            assert response.json['boarding'] == None
            assert response.json['dueDate'] == None

            when(
                'Manager id not in form',
                form=given - 'managerId' | dict(title='1')
            )
            assert status == '734 Manager Id Not In Form'

            when(
                'Manager not found with string type',
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

            with chat_server_status('615 Room Already Exists'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(title='Another title')
                )
                assert status == '200 OK'

            with chat_server_status('604 Already Added To Target'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(title='Awesome project')
                )
                assert status == '200 OK'

    def test_update(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Updating a project',
            '/apiv1/projects/id:2',
            'UPDATE',
            form=dict(
                title='My interesting project',
                description='A updated project description',
                status='active',
                managerId=2,
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting project'
            assert response.json['description'] == 'A updated project ' \
                'description'
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
                'Manager not found with string type',
                form=given | dict(managerId='Alphabetical', title='1')
            )
            assert status == 608
            assert status.text.startswith('Manager not found')

            when(
                'Manager is not found',
                form=Update(managerId=100)
            )
            assert status == 608
            assert status.text.startswith('Manager not found')

            when(
                'Title is repetetive',
                form=Update(title='My hidden project')
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

            when('Request is not authorized', authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    form=given | dict(managerId=3)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    form=given | dict(managerId=3)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(managerId=3)
                )
                assert status == '801 Chat Server Internal Error'

            with room_mockup_server():
                when(
                    'Room member is already added to room',
                    form=given | dict(managerId=3)
                )
                assert status == '200 OK'

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

        with oauth_mockup_server(), self.given(
            'Showing a unhidden project',
            '/apiv1/projects/id:4',
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

        with oauth_mockup_server(), self.given(
            'List projects',
            '/apiv1/projects',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 6

            with self.given(
                'Sort projects by phases title',
                '/apiv1/projects',
                'LIST',
                query=dict(sort='title')
            ):
                assert status == 200
                assert response.json[0]['title'] == 'Another title'

                when(
                    'Reverse sorting titles by alphabet',
                    query=dict(sort='-title')
                )
                assert response.json[0]['title'] == 'My second project'

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
                assert response.json[0]['title'] == 'My hidden project'

                when(
                    'Manipulate sorting and pagination',
                    query=dict(sort='-title', take=1, skip=2)
                )
                assert response.json[0]['title'] == 'My hidden project'

                when('Request is not authorized', authorization=None)
                assert status == 401

    def test_subscribe(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
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
                'Project is already subscribed',
                url_parameters=dict(id=4),
                form=given | dict(memberId=1)
            )
            assert status == '611 Already Subscribed'

            when('Request is not authorized', authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    url_parameters=dict(id=2)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=2)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=2)
                )
                assert status == '801 Chat Server Internal Error'

            with room_mockup_server():
                when(
                    'Room member is already added to room',
                    url_parameters=dict(id=2)
                )
                assert status == '200 OK'

    def test_unsubscribe(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
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

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    url_parameters=dict(id=2)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=2)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=2)
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('611 Room Member Not Found'):
                when(
                    'Room member not found',
                    url_parameters=dict(id=2)
                )
                assert status == '200 OK'

