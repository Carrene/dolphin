
from bddrest import status, response, Update, when, Remove, Append

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Project, Manager, Release


class TestManager(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        manager = Manager(
            title='First Manager',
            email=None,
            phone=123456789
        )
        session.add(manager)
        session.flush()

        release = Release(
            manager_id=manager.id,
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release)
        session.flush()

        project = Project(
            manager_id=manager.id,
            release_id=release.id,
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



