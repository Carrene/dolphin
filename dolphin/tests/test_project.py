
from bddrest import status, response, Update, when, Remove

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.controllers.root import Root
from dolphin.models import Project, Administrator, Release


class TestProject(LocalApplicationTestCase):
    __controller_factory__ = Root


    @classmethod
    def mockup(cls):
        session = cls.create_session()

        administrator = Administrator(
            title='First Administrator',
            email=None,
            phone=123456789
        )
        session.add(administrator)
        session.commit()

        release = Release(
            administrator_id=administrator.id,
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release)
        session.commit()

        project = Project(
            administrator_id=administrator.id,
            release_id=release.id,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
        )
        session.add(project)
        session.flush()
        cls.administrator_id = administrator.id
        cls.release_id = release.id
        session.commit()

    def test_create(self):
        with self.given(
            'Createing a project',
            '/apiv1/projects',
            'CREATE',
            form=dict(
                administratorId=self.administrator_id,
                releaseId=self.release_id,
                title='My awesome project',
                description='A decription for my project',
                dueDate='2020-2-20'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome project'
            assert response.json['description'] == 'A decription for my project'
            assert response.json['dueDate'] == '2020-02-20T00:00:00'
            assert response.json['status'] is None

            when(
                'Title is not in form',
                form=Remove('title')
            )
            assert status == '710 Title not exists'

            when(
                'Title length is more than limit',
                form=Update(
                    title='This is a title with the length more than 50 '\
                    'characters'
                )
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Description length is less than limit',
                form=Update(description='Description')
            )
            assert status == '703 At least 20 characters are needed for '\
                'description'

            when(
                'Due date format is wrong',
                form=Update(dueDate='20-20-20')
            )
            assert status == '701 Invalid due date format'

            when(
                'Due date is not in form',
                form=Remove('dueDate')
            )
            assert status == '711 Due date not exists'


