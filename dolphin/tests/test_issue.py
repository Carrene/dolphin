
from bddrest import status, response, Update, when, Remove, Append, given_form

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Issue, Project, Manager, Release, Phase
# FIXME: remove this line
from dolphin.models import Association


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        manager = Manager(
            title='First Manager',
            email=None,
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
            releases=release,
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
        )

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1
        )

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )

        issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of third issue',
            due_date='2020-2-20',
            kind='feature',
            days=3
        )

        issue4 = Issue(
            project=project,
            title='Fourth issue',
            description='This is description of fourth issue',
            due_date='2020-2-20',
            kind='feature',
            days=4
        )

        cls.project = project
        session.add(project)
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
                'Project id not in form',
                form=given_form - 'projectId' | dict(title='1')
            )
            assert status == '713 Project id not in form'

            when(
                'Project not found with string type',
                form=given_form | dict(projectId='Alphabetical', title='1')
            )
            assert status == '714 Invalid project id type'

            when(
                'Project not found with integer type',
                form=given_form | dict(projectId=100, title='1')
            )
            assert status == 601
            assert status.text.startswith('Project not found')

            when(
                'Title is not in form',
                form=given_form - 'title'
            )
            assert status == '710 Title not in form'

            when(
                'Title is repetitive',
                form=Update(title='First issue')
            )
            assert status == 600
            assert status.text.startswith('Another issue with title')

            when(
                'Title length is more than limit',
                form=given_form | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Description length is less than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title=('Another title')
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
                form=given_form - 'dueDate' | dict(title='Another title')
            )
            assert status == '711 Due date not in form'

            when(
                'Kind is not in form',
                form=given_form - 'kind' | dict(title='Another title')
            )
            assert status == '718 Kind not in form'

            when(
                'Days is not in form',
                form=given_form - 'days' | dict(title='Another title')
            )
            assert status == '720 Days not in form'

            when(
                'Days type is wrong',
                form=given_form | dict(
                    days='Alphabetical',
                    title='Another title'
                )
            )
            assert status == '721 Invalid days type'

            when(
                'Invalid kind value is in form',
                form=given_form | dict(kind='enhancing', title='Another title')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=given_form + dict(status='progressing') | \
                    dict(title='Another title')
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
                url_parameters=dict(id='Alphabetical'),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Title is repetitive',
                form=given_form | dict(title='Defined issue')
            )
            assert status == 600
            assert status.text.startswith('Another issue with title')
            when(
                'Title length is more than limit',
                form=given_form | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Description length is less than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title=('Another title')
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
                'Invalid kind value is in form',
                form=given_form | dict(kind='enhancing', title='Another title')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=given_form + dict(status='progressing') | \
                    dict(title='Another title')
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when(
                'Invalid parameter is in the form',
                form=given_form + dict(invalid_param='External parameter') | \
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


    def test_list(self):
        with self.given(
            'List issues',
            '/apiv1/issues',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 5

        with self.given(
            'Sort issues by title',
            '/apiv1/issues',
            'LIST',
            query=dict(sort='title')
        ):
            assert response.json[0]['title'] == 'Defined issue'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'Third issue'

        with self.given(
            'Filter issues',
            '/apiv1/issues',
            'LIST',
            query=dict(title='Defined issue')
        ):
            assert response.json[0]['title'] == 'Defined issue'

            when(
                'List issues except one of them',
                query=dict(title='!Defined issue')
            )
            assert response.json[0]['title'] == 'Second issue'

        with self.given(
             'Issues pagination',
             '/apiv1/issues',
             'LIST',
             query=dict(take=1, skip=3)
         ):
            assert response.json[0]['title'] == 'Defined issue'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'New issue'


    def test_subscribe(self):
        with self.given(
            'Subscribe an issue',
            '/apiv1/issues/id:4',
            'SUBSCRIBE',
            form=dict(memberId=1)
        ):
            assert status == 200

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given_form | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Member id not in form',
                form=given_form - 'memberId'
            )
            assert status == '735 Member id not in form'

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
            assert status == '736 Invalid member id type'

            when(
                'Issue is already subscribed',
                url_parameters=dict(id=4),
                form=given_form | dict(memberId=1)
            )
            assert status == '611 Already subscribed'

