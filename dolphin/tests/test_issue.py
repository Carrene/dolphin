
from bddrest import status, response, Update, when, Remove, Append, given

from dolphin.models import Issue, Project, Manager, Release, Phase, Resource
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        manager = Manager(
            title='First Manager',
            email='manager1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )

        resource = Resource(
            title='First Resource',
            email='resource1@example.com',
            access_token='access token 2',
            phone=987654321,
            reference_id=2
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
            room_id=1
        )

        phase = Phase(
            title='development',
            order=2,
            project=project
        )

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1
        )

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )

        issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of third issue',
            due_date='2020-2-20',
            kind='feature',
            days=3
        )

        issue4 = Issue(
            project=project,
            title='Fourth issue',
            description='This is description of fourth issue',
            due_date='2020-2-20',
            kind='feature',
            days=4
        )

        cls.project = project
        session.add_all([project, resource, phase])
        session.commit()

    def test_define(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Define an issue',
            '/apiv1/issues',
            'DEFINE',
            form=dict(
                title='Defined issue',
                description='A description for defined issue',
                dueDate='2200-2-20',
                kind='enhancement',
                days=3,
                projectId=self.project.id,
            )
        ):
            assert status == 200
            assert response.json['title'] == 'Defined issue'
            assert response.json['description'] == 'A description for '\
                'defined issue'
            assert response.json['dueDate'] == '2200-02-20T00:00:00'
            assert response.json['kind'] == 'enhancement'
            assert response.json['days'] == 3
            assert response.json['status'] == 'triage'

            when(
                'Project id not in form',
                form=given - 'projectId' | dict(title='1')
            )
            assert status == '713 Project Id Not In Form'

            when(
                'Project not found with string type',
                form=given | dict(projectId='Alphabetical', title='1')
            )
            assert status == '714 Invalid Project Id Type'

            when(
                'Project not found with integer type',
                form=given | dict(projectId=100, title='1')
            )
            assert status == 601
            assert status.text.startswith('Project not found')

            when(
                'Title is not in form',
                form=given - 'title'
            )
            assert status == '710 Title Not In Form'

            when(
                'Title is repetitive',
                form=Update(title='First issue')
            )
            assert status == 600
            assert status.text.startswith('Another issue with title')

            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                    title=('Another title')
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
                form=given - 'dueDate' | dict(title='Another title')
            )
            assert status == '711 Due Date Not In Form'

            when(
                'Kind is not in form',
                form=given - 'kind' | dict(title='Another title')
            )
            assert status == '718 Kind Not In Form'

            when(
                'Days is not in form',
                form=given - 'days' | dict(title='Another title')
            )
            assert status == '720 Days Not In Form'

            when(
                'Days type is wrong',
                form=given | dict(
                    days='Alphabetical',
                    title='Another title'
                )
            )
            assert status == '721 Invalid Days Type'

            when(
                'Invalid kind value is in form',
                form=given | dict(kind='enhancing', title='Another title')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=given + dict(status='progressing') | \
                    dict(title='Another title')
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when('Request is not authorized',authorization=None)
            assert status == 401

    def test_update(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Update a issue',
            '/apiv1/issues/id:3',
            'UPDATE',
            form=dict(
                title='New issue',
                description='This is a description for new issue',
                dueDate='2200-12-12',
                kind='feature',
                days=4,
            )
        ):
            assert status == 200

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Title is repetitive',
                form=given | dict(title='Defined issue')
            )
            assert status == 600
            assert status.text.startswith('Another issue with title')
            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                    title=('Another title')
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
                'Invalid kind value is in form',
                form=given | dict(kind='enhancing', title='Another title')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=given + dict(status='progressing') | \
                    dict(title='Another title')
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when(
                'Invalid parameter is in the form',
                form=given + dict(invalid_param='External parameter') | \
                    dict(title='Another title')
            )
            assert status == 707
            assert status.text.startswith('Invalid field')

            when('Request is not authorized',authorization=None)
            assert status == 401

        with oauth_mockup_server(), self.given(
            'Updating project with empty form',
            '/apiv1/issues/id:2',
            'UPDATE',
            form=dict()
        ):
            assert status == '708 No Parameter Exists In The Form'

    def test_list(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'List issues',
            '/apiv1/issues',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 5

        with oauth_mockup_server(), self.given(
            'Sort issues by title',
            '/apiv1/issues',
            'LIST',
            query=dict(sort='title')
        ):
            assert response.json[0]['title'] == 'Defined issue'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'Third issue'

        with oauth_mockup_server(), self.given(
            'Filter issues',
            '/apiv1/issues',
            'LIST',
            query=dict(title='Defined issue')
        ):
            assert response.json[0]['title'] == 'Defined issue'

            when(
                'List issues except one of them',
                query=dict(title='!Defined issue')
            )
            assert response.json[0]['title'] == 'Second issue'

        with oauth_mockup_server(), self.given(
             'Issues pagination',
             '/apiv1/issues',
             'LIST',
             query=dict(take=1, skip=3)
         ):
            assert response.json[0]['title'] == 'Defined issue'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'New issue'

            when('Request is not authorized',authorization=None)
            assert status == 401

    def test_subscribe(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Subscribe an issue',
            '/apiv1/issues/id:4',
            'SUBSCRIBE',
            form=dict(memberId=1, authorizationCode='authorization code')
        ):
            assert status == 200

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given | dict(title='Another issue')
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

            when('Request is not authorized',authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    url_parameters=dict(id=3)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=3)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=3)
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('604 Already Added To Target'):
                when(
                    'Member is already added to room',
                    url_parameters=dict(id=3)
                )
                assert status == '200 OK'

    def test_unsubscribe(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Unsubscribe an issue',
            '/apiv1/issues/id:4',
            'UNSUBSCRIBE',
            form=dict(memberId=1, authorizationCode='authorization code')
        ):
            assert status == 200

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given | dict(title='Another issue')
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

            when('Request is not authorized',authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    url_parameters=dict(id=3)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=3)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=3)
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('611 Room Member Not Found'):
                when(
                    'Room member not found',
                    url_parameters=dict(id=3)
                )
                assert status == '200 OK'

    def test_assign(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Assign an issue to a resource',
            '/apiv1/issues/id:4',
            'ASSIGN',
            form=dict(resourceId=2, phaseId=1)
        ):
            assert status == 200

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Resource not found',
                form=given | dict(resourceId=100)
            )
            assert status == 609
            assert status.text.startswith('Resource not found')

            when(
                'Resource id is not in form',
                form=given - 'resourceId'
            )
            assert status == '715 Resource Id Not In Form'

            when(
                'Resource id type is not valid',
                form=given | dict(resourceId='Alphabetical')
            )
            assert status == '716 Invalid Resource Id Type'

            when(
                'Phase not found',
                form=given | dict(phaseId=100)
            )
            assert status == 613
            assert status.text.startswith('Phase not found')

            when(
                'Phase id is not in form',
                form=given - 'phaseId'
            )
            assert status == '737 Phase Id Not In Form'

            when(
                'Phase id type is not valid',
                form=given | dict(phaseId='Alphabetical')
            )
            assert status == '738 Invalid Phase Id Type'

            when(
                'Issue is already assigned',
                url_parameters=dict(id=4),
                form=given | dict(resourceId=2)
            )
            assert status == '602 Already Assigned'

            when('Request is not authorized',authorization=None)
            assert status == 401

