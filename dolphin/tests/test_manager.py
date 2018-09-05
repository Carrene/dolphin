
from bddrest import status, response, Update, when, Remove, Append, given_form

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Project, Manager, Release


class TestManager(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        assigned_manager = Manager(
            title='Assigned Manager',
            email='assigned@example.com',
            password='123456',
            phone=123456789
        )

        unassigned_manager = Manager(
            title='Unassigned Manager',
            email='unassigned@example.com',
            password='123456',
            phone=987654321
        )

        manager1 = Manager(
            title='First Manager',
            email='manager1@example.com',
            password='123456',
            phone=123987465
        )
        session.add(manager1)

        manager2 = Manager(
            title='Second Manager',
            email='manager2@example.com',
            password='123456',
            phone=1287465
        )
        session.add(manager2)

        manager3 = Manager(
            title='Third Manager',
            email='manager3@example.com',
            password='123456',
            phone=128973465
        )
        session.add(manager3)

        manager4 = Manager(
            title='Fourth Manager',
            email='manager4@example.com',
            password='123456',
            phone=1289733465
        )
        session.add(manager4)

        release = Release(
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        project = Project(
            manager=assigned_manager,
            releases=[release],
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
        )
        session.add(project)
        session.commit()

    def test_assign(self):
        with self.given(
            'Assign a manager to project',
            '/apiv1/managers/id:1',
            'ASSIGN',
            form=dict(projectId='1')
        ):
            assert status == 200

            when(
                'Intended manager with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended manager with integer type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Project id not in form',
                form=given_form - 'projectId'
            )
            assert status == '713 Project Id Not In Form'

            when(
                'Project id type is invalid',
                form=given_form | dict(projectId='Alphabetical')
            )
            assert status == '714 Invalid Project Id Type'

            when(
                'Project not found with integer type',
                form=given_form | dict(projectId=100)
            )
            assert status == 601
            assert status.text.startswith('Project not found')

    def test_list(self):
        with self.given(
            'List managers',
            '/apiv1/managers',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 5

        with self.given(
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
            assert response.json[0]['title'] == 'Third Manager'

        with self.given(
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

        with self.given(
            'Manager pagination',
            '/apiv1/managers',
            'LIST',
            query=dict(sort='id', take=1, skip=2)
        ):
            assert response.json[0]['title'] == 'Third Manager'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'Fourth Manager'

