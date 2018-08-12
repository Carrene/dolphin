
from bddrest import status, response, Update, when, Remove, Append, given_form

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Project, Manager, Release


class TestManager(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        assigned_manager = Manager(
            title='First Manager',
            email=None,
            phone=123456789
        )

        unassigned_manager = Manager(
            title='Second Manager',
            email=None,
            phone=987654321
        )

        release = Release(
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        project = Project(
            manager=assigned_manager,
            releases=release,
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
            form=dict(projectId='2')
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
            assert status == '713 Project id not in form'

            when(
                'Project id type is invalid',
                form=given_form | dict(projectId='Alphabetical')
            )
            assert status == '714 Invalid project id type'

            when(
                'Project not found with integer type',
                form=given_form | dict(projectId=100)
            )
            assert status == 601
            assert status.text.startswith('Project not found')

