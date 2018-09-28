from bddrest import status, response, Update, when, Remove, Append, given

from dolphin.models import Release, Manager, Project
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server

class TestRelease(LocalApplicationTestCase):

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

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release1)

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release2)

        release3 = Release(
            title='My third release',
            description='A decription for my third release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release3)

        release4 = Release(
            title='My fourth release',
            description='A decription for my fourth release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release4)

        project1 = Project(
            manager=manager,
            release=release1,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
            room_id=1000
        )
        session.add(project1)

        project2 = Project(
            manager=manager,
            release=release1,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
            room_id=1000
        )
        session.add(project2)

        project3 = Project(
            manager=manager,
            release=release1,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
            room_id=1000
        )
        session.add(project3)

        project4 = Project(
            manager=manager,
            release=release1,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
            room_id=1000
        )
        session.add(project4)
        session.commit()

    def test_create(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Createing a release',
            '/apiv1/releases',
            'CREATE',
            form=dict(
                title='My awesome release',
                description='Decription for my release',
                dueDate='2020-2-20',
                cutoff='2030-2-20'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome release'
            assert response.json['description'] == 'Decription for my release'
            assert response.json['dueDate'] == '2020-02-20T00:00:00'
            assert response.json['cutoff'] == '2030-02-20T00:00:00'
            assert response.json['status'] is None

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
                form=given - 'dueDate' | dict(title='Another title')
            )
            assert status == '711 Due Date Not In Form'

            when(
                'Cutoff format is wrong',
                form=given | dict(
                    cutoff='30-20-20',
                    title='Another title'
                )
            )
            assert status == '702 Invalid Cutoff Format'

            when(
                'Due date is not in form',
                form=given - 'cutoff' | dict(title='Another title')
            )
            assert status == '712 Cutoff Not In Form'

            when(
                'Invalid status in form',
                form=given | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_update(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Updating a release',
            '/apiv1/releases/id:1',
            'UPDATE',
            form=dict(
                title='My interesting release',
                description='This is my new awesome release',
                dueDate='2200-2-2',
                cutoff='2300-2-2',
                status='in-progress'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting release'
            assert response.json['description'] == 'This is my new awesome release'
            assert response.json['dueDate'] == '2200-02-02T00:00:00'
            assert response.json['cutoff'] == '2300-02-02T00:00:00'
            assert response.json['status'] == 'in-progress'

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                form=given | dict(title='Another title'),
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Title is repetitive',
                form=given | dict(title='My second release')
            )
            assert status == 600
            assert status.text.startswith('Another release with title')

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For '\
                'Description'

            when(
                'Due date format is wrong',
                form=given | dict(
                    dueDate='20-20-20',
                )
            )
            assert status == '701 Invalid Due Date Format'

            when(
                'Cutoff format is wrong',
                form=given | dict(
                    cutoff='30-20-20',
                )
            )
            assert status == '702 Invalid Cutoff Format'

            when(
                'Invalid status in form',
                form=given | dict(
                    status='progressing',
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when('Request is not authorized', authorization=None)
            assert status == 401

        with oauth_mockup_server(), self.given(
            'Send HTTP request with empty form parameter',
            '/apiv1/releases/id:1',
            'UPDATE',
            form=dict()
        ):
            assert status == '708 No Parameter Exists In The Form'

    def test_abort(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Aborting a release',
            '/apiv1/releases/id:2',
            'ABORT'
        ):
            assert status == 200

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            session = self.create_session()
            release = session.query(Release) \
                .filter(Release.id == 2) \
                .one_or_none()
            assert release is None

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_list(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'List releases',
            '/apiv1/releases',
            'LIST'
        ):
            assert status == 200
            assert len(response.json) == 4

        with oauth_mockup_server(), self.given(
            'Sort releases by title',
            '/apiv1/releases',
            'LIST',
            query=dict(sort='title')
        ):
            assert response.json[0]['title'] == 'My awesome release'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'My third release'

        with oauth_mockup_server(), self.given(
            'Filter releases',
            '/apiv1/releases',
            'LIST',
            query=dict(sort='id', take=1, skip=2)
        ):
            assert response.json[0]['title'] == 'My fourth release'

            when(
                'List releases except one of them',
                query=dict(title='!My second release')
            )
            assert response.json[0]['title'] == 'My third release'

        with oauth_mockup_server(), self.given(
             'Issues pagination',
             '/apiv1/releases',
             'LIST',
             query=dict(sort='id', take=1, skip=2)
         ):
            assert response.json[0]['title'] == 'My fourth release'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'My fourth release'

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_subscribe(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Subscribe release',
            '/apiv1/releases/id:1',
            'SUBSCRIBE',
            form=dict(memberId=1, authorizationCode='authorization code')
        ):
            assert status == 200

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                url_parameters=dict(id=100)
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
                url_parameters=dict(id=1),
                form=given | dict(memberId=1)
            )
            assert status == '611 Already Subscribed'

            when('Request is not authorized', authorization=None)
            assert status == 401

#            with chat_server_status('404 Not Found'):
#                when('Chat server is not found')
#                assert status == '617 Chat Server Not Found'
#
#            with chat_server_status('503 Service Not Available'):
#                when('Chat server is not available')
#                assert status == '800 Chat Server Not Available'
#
#            with chat_server_status('500 Internal Service Error'):
#                when('Chat server faces with internal error')
#                assert status == '801 Chat Server Internal Error'
#
#            with chat_server_status('604 Already Added To Target'):
#                when('Member is already added to room')
#                assert status == '200 OK'

    def test_unsubscribe(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Unsubscribe release',
            '/apiv1/releases/id:1',
            'UNSUBSCRIBE',
            form=dict(memberId=1, authorizationCode='authorization code')
        ):
            assert status == 200

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                url_parameters=dict(id=100)
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
                url_parameters=dict(id=1),
                form=given | dict(memberId=1)
            )
            assert status == '612 Not Subscribed Yet'

            when('Request is not authorized', authorization=None)
            assert status == 401

#            with chat_server_status('404 Not Found'):
#                when('Chat server is not found')
#                assert status == '617 Chat Server Not Found'
#
#            with chat_server_status('503 Service Not Available'):
#                when('Chat server is not available')
#                assert status == '800 Chat Server Not Available'
#
#            with chat_server_status('500 Internal Service Error'):
#                when('Chat server faces with internal error')
#                assert status == '801 Chat Server Internal Error'
#
#            with chat_server_status('611 Member Not Found'):
#                when('Room member is not found')
#                assert status == '200 OK'

