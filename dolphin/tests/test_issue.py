
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

        stage = Stage(
            project=project,
            title='triage',
            order=0
        )
        session.add(stage)
        session.flush()

        issue = Issue(
            project=project,
            stage=stage,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )

        cls.project = project
        cls.stage = stage
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
                stageId=self.stage.id
            )
        ):
            assert status == 200
            assert response.json['title'] == 'Defined issue'
            assert response.json['description'] == 'A description for '\
                'defined issue'
            assert response.json['dueDate'] == '2200-02-20T00:00:00'
            assert response.json['kind'] == 'enhancement'
            assert response.json['days'] == 3
            assert response.json['status'] == None

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

