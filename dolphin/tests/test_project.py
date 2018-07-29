
from bddrest import status, response, Update, when, Remove

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.controllers.root import Root
from dolphin.models import Project, Administrator, Release


long_invalid_string = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod \
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, \
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo \
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse \
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non \
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Sed \
ut perspiciatis unde omnis iste natus error sit voluptatem accusantium \
doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore \
veritatis et quasi architecto beatae vitae dicta sunt explicabo.
'''


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
                form=Update(description=long_invalid_string)
            )
            assert status == '703 At most 512 characters are valid for '\
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


