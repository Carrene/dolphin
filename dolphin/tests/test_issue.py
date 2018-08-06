
from bddrest import status, response, Update, when, Remove, Append

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Issue, Project, Manager, Release, Stage


class TestIssue(LocalApplicationTestCase):

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
            manager=manager,
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release)
        session.flush()

        project = Project(
            manager=manager,
            releases=release,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
        )
        session.add(project)
        session.flush()

        issue = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )

        cls.project = project
        session.add(issue)
        session.commit()

    def test_define(self):
        with self.given(
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
                'Title is not in form',
                form=Remove('title')
            )
            assert status == '710 Title not in form'

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
                form=Update(description=((512 + 1) * 'a'))
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
            assert status == '711 Due date not in form'

            when(
                'Kind is not in form',
                form=Remove('kind')
            )
            assert status == '718 Kind not in form'

            when(
                'Days is not in form',
                form=Remove('days')
            )
            assert status == '720 Days not in form'

            when(
                'Days type is wrong',
                form=Update(days='Alphabetical')
            )
            assert status == '721 Invalid days type'
            when(
                'Title is repetitive',
                form=Update(title='First issue')
            )
            assert status == 600
            assert status.text.startswith('Another project with title')

            when(
                'Invalid kind value is in form',
                form=Update(kind='enhancing')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=Append(status='progressing')
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

    def test_update(self):
        with self.given(
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
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

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
                form=Update(description=((512 + 1) * 'a'))
            )
            assert status == '703 At most 512 characters are valid for '\
                'description'

            when(
                'Due date format is wrong',
                form=Update(dueDate='20-20-20')
            )
            assert status == '701 Invalid due date format'

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Invalid kind value is in form',
                form=Update(kind='enhancing')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=Append(status='progressing')
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when(
                'Title is repetitive',
                form=Update(title='Defined issue')
            )
            assert status == 600
            assert status.text.startswith('Another project with title')

            when(
                'Invalid parameter is in the form',
                form=Append(invalid_param='This is an external parameter')
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

