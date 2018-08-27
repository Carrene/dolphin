
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
            password='123456',
            phone=123456789
        )

        release = Release(
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        project = Project(
            manager=manager,
            releases=[release],
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
        )

        hidden_project = Project(
            manager=manager,
            releases=[release],
            title='My hidden project',
            description='A decription for my project',
            due_date='2020-2-20',
            removed_at='2020-2-20'
        )

        session.add_all([manager, project, hidden_project, release])
        session.commit()
        cls.manager_id = manager.id
        cls.release = release

    def test_create(self):
        with self.given(
            'Createing a project',
            '/apiv1/projects',
            'CREATE',
            form=dict(
                managerId=self.manager_id,
                releases=self.release,
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
            assert status == '734 Manager Id Not In Form'

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
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                form=given_form | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For '\
                'Description'

            when(
                'Due date format is wrong',
                form=given_form | dict(
                    dueDate='20-20-20',
                    title='Another title'
                )
            )
            assert status == '701 Invalid Due Date Format'

            when(
                'Due date is not in form',
                form=given_form - ['dueDate'] | dict(title='Another title')
            )

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
            '/apiv1/projects/id:1',
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
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is more than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when(
                'Due date format is wrong',
                form=given_form | dict(
                    dueDate='2200-2-32',
                    title='Another title'
                )
            )
            assert status == '701 Invalid Due Date Format'

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
            assert status == '708 No Parameter Exists In The Form'

    def test_hide(self):
        with self.given(
            'Hiding a project',
            '/apiv1/projects/id:1',
            'HIDE'
        ):
            session = self.create_session()
            project = session.query(Project) \
                .filter(Project.id == 1) \
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
            assert status == '709 Form Not Allowed'

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

    def test_subscribe(self):
        with self.given(
            'Subscribe project',
            '/apiv1/projects/id:4',
            'SUBSCRIBE',
            form=dict(memberId=1)
        ):
            assert status == 200

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended project with integer type not found',
                url_parameters=dict(id=100),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Member id not in form',
                form=given_form - 'memberId'
            )
            assert status == '735 Member Id Not In Form'

            when(
                'Member not found',
                form=given_form | dict(memberId=100)
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member id type is invalid',
                form=given_form | dict(memberId='Alphabetical')
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'Issue is already subscribed',
                url_parameters=dict(id=4),
                form=given_form | dict(memberId=1)
            )
            assert status == '611 Already Subscribed'

    def test_unsubscribe(self):
        with self.given(
            'Unsubscribe an project',
            '/apiv1/projects/id:4',
            'UNSUBSCRIBE',
            form=dict(memberId=1)
        ):
            assert status == 200

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended project with integer type not found',
                url_parameters=dict(id=100),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Member id not in form',
                form=given_form - 'memberId'
            )
            assert status == '735 Member Id Not In Form'

            when(
                'Member not found',
                form=given_form | dict(memberId=100)
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member id type is invalid',
                form=given_form | dict(memberId='Alphabetical')
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'Issue is not subscribed yet',
                url_parameters=dict(id=4),
                form=given_form | dict(memberId=1)
            )
            assert status == '612 Not Subscribed Yet'

