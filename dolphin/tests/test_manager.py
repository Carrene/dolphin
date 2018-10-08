from bddrest import status, response, Update, when, Remove, Append, given

from dolphin.models import Project, Manager, Release, Member
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestManager(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123457869,
            reference_id=5
        )
        session.add(cls.member1)


        assigned_manager = Manager(
            title='Assigned Manager',
            email='assigned@example.com',
            access_token='access token 3',
            phone=123456789,
            reference_id=1
        )
        session.add(assigned_manager)

        unassigned_manager = Manager(
            title='Unassigned Manager',
            email='unassigned@example.com',
            access_token='access token 2',
            phone=987654321,
            reference_id=2
        )
        session.add(unassigned_manager)

        manager1 = Manager(
            title='First Manager',
            email='manager1@example.com',
            access_token='access token 1',
            phone=123987465,
            reference_id=3
        )
        session.add(manager1)

        manager2 = Manager(
            title='Second Manager',
            email='manager2@example.com',
            access_token='access token',
            phone=1287465,
            reference_id=4
        )
        session.add(manager2)

        release = Release(
            title='My first release',
            description='A decription for my release',
            cutoff='2030-2-20',
        )

        project = Project(
            manager=assigned_manager,
            release=release,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)
        session.commit()

    def test_list(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'List managers',
            '/apiv1/managers',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 4

        with oauth_mockup_server(), self.given(
            'Sort managers by title',
            '/apiv1/managers',
            'LIST',
            query=dict(sort='title')
        ):
            assert status == 200
            assert response.json[0]['title'] == 'Assigned Manager'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'Unassigned Manager'

        with oauth_mockup_server(), self.given(
            'Filter managers',
            '/apiv1/managers',
            'LIST',
            query=dict(sort='id', title='First Manager')
        ):
            assert response.json[0]['title'] == 'First Manager'

            when(
                'List managers except one of them',
                query=dict(title='!Assigned Manager')
            )
            assert response.json[0]['title'] != 'Assigned Manager'

        with oauth_mockup_server(), self.given(
            'Manager pagination',
            '/apiv1/managers',
            'LIST',
            query=dict(sort='id', take=1, skip=2)
        ):
            assert response.json[0]['title'] == 'First Manager'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'First Manager'

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_make(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Make a manager',
            f'/apiv1/members/{self.member1.id}/managers',
            'MAKE',
        ):
            assert status == 200



