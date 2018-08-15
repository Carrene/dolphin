
from bddrest import status, response, Update, when, Remove, Append, given_form

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Project, Manager, Release


class TestProject(LocalApplicationTestCase):

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
        session.flush()

        hidden_project = Project(
            manager_id=manager.id,
            release_id=release.id,
            title='My hidden project',
            description='A decription for my project',
            due_date='2020-2-20',
            removed_at='2020-2-20'
        )
        session.add(hidden_project)

        cls.manager_id = manager.id
        cls.release_id = release.id
        session.commit()

    def test_create(self):
        with self.given(
            'Createing a project',
            '/apiv1/projects',
            'CREATE',
            form=dict(
                managerId=self.manager_id,
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
                'Manager id not in form',
                form=given_form - 'managerId' | dict(title='1')
            )
            assert status == '734 Manager id not in form'

            when(
                'Manger not found with string type',
                form=given_form | dict(managerId='Alphabetical', title='1')
            )
            assert status == 608
            assert status.text.startswith('Manager not found')

            when(
                'Manager not found with integer type',
                form=given_form | dict(managerId=100, title='1')
            )
            assert status == 608
            assert status.text.startswith('Manager not found')

            when(
                'Release not found with string type',
                form=given_form | dict(releaseId='Alphabetical', title='1')
            )
            assert status == 607
            assert status.text.startswith('Release not found')

            when(
                'Release not found with integer type',
                form=given_form | dict(releaseId=100, title='1')
            )
            assert status == 607
            assert status.text.startswith('Release not found')

            when(
                'Title is not in form',
                form=Remove('title')
            )
            assert status == '710 Title not in form'

            when(
                'Title length is more than limit',
                form=given_form | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Description length is less than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At most 512 characters are valid for '\
                'description'

            when(
                'Due date format is wrong',
                form=given_form | dict(
                    dueDate='20-20-20',
                    title='Another title'
                )
            )
            assert status == '701 Invalid due date format'

            when(
                'Due date is not in form',
                form=given_form - ['dueDate'] | dict(title='Another title')
            )
            assert status == '711 Due date not in form'

            when(
                'Status value is invalid',
                form=given_form | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')


    def test_update(self):
        with self.given(
            'Updating a project',
            '/apiv1/projects/id:2',
            'UPDATE',
            form=dict(
                title='My interesting project',
                description='A updated project description',
                dueDate='2200-2-20',
                status='in-progress'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting project'
            assert response.json['description'] == 'A updated project ' \
                'description'
            assert response.json['dueDate'] == '2200-02-20T00:00:00'
            assert response.json['status'] == 'in-progress'

            when(
                'Intended project with string type not found',
                form=given_form | dict(title='Another title'),
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                form=given_form | dict(title='Another title'),
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title is repetetive',
                form=Update(title='My interesting project')
            )
            assert status == 600
            assert status.text.startswith('Another project with title')

            when(
                'Title length is more than limit',
                form=Update(
                    title=((50 + 1) * 'a')
                )
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Description length is more than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At most 512 characters are valid for ' \
                'description'

            when(
                'Due date format is wrong',
                form=given_form | dict(
                    dueDate='2200-2-32',
                    title='Another title'
                )
            )
            assert status == '701 Invalid due date format'

            when(
                'Status value is invalid',
                form=given_form | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when(
                'Invalid parameter is in the form',
                form=given_form + \
                    dict(invalid_param='External parameter') | \
                    dict(title='Another title')
            )
            assert status == 707
            assert status.text.startswith('Invalid field')

        with self.given(
            'Updating project with empty form',
            '/apiv1/projects/id:2',
            'UPDATE',
            form=dict()
        ):
            assert status == '708 No parameter exists in the form'

    def test_hide(self):
        with self.given(
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
                'Intended project with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when('Project not found', url_parameters=dict(id=100))
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form not allowed'

    def test_show(self):
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
            assert status == '709 Form not allowed'

    def test_list(self):
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

