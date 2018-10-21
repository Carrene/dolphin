from bddrest import status, response, Update, when, given

from dolphin.models import Issue, Project, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )

        workflow = Workflow(title='First Workflow')

        project = Project(
            member=member,
            workflow=workflow,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1
        )
        session.add(issue1)
        session.commit()
        cls.project = project

    def test_define(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
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
                form=given - 'projectId' | dict(title='New title')
            )
            assert status == '713 Project Id Not In Form'

            when(
                'Project not found with string type',
                form=given | dict(projectId='Alphabetical', title='New title')
            )
            assert status == '714 Invalid Project Id Type'

            when(
                'Project not found with integer type',
                form=given | dict(projectId=100, title='New title')
            )
            assert status == 601
            assert status.text.startswith('Project not found')

            when(
                'Title is not in form',
                form=given - 'title'
            )
            assert status == '710 Title Not In Form'

            when(
                'Title format is wrong',
                form=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title is repetitive',
                form=Update(title='First issue')
            )
            assert status == 600
            assert status.text.startswith('Another issue with title')

            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                    title=('Another title')
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For '\
                'Description'

            when(
                'Due date format is wrong',
                form=given | dict(
                    dueDate='20-20-20',
                    title='Another title'
                )
            )
            assert status == '701 Invalid Due Date Format'

            when(
                'Due date is not in form',
                form=given - 'dueDate' | dict(title='Another title')
            )
            assert status == '711 Due Date Not In Form'

            when(
                'Kind is not in form',
                form=given - 'kind' | dict(title='Another title')
            )
            assert status == '718 Kind Not In Form'

            when(
                'Days is not in form',
                form=given - 'days' | dict(title='Another title')
            )
            assert status == '720 Days Not In Form'

            when(
                'Days type is wrong',
                form=given | dict(
                    days='Alphabetical',
                    title='Another title'
                )
            )
            assert status == '721 Invalid Days Type'

            when(
                'Invalid kind value is in form',
                form=given | dict(kind='enhancing', title='Another title')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=given + dict(status='progressing') | \
                    dict(title='Another title')
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when('Request is not authorized', authorization=None)
            assert status == 401

