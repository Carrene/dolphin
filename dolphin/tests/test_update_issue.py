from auditing.context import Context as AuditLogContext
from bddrest import status, when, given, response, Update

from dolphin.models import Issue, Project, Member, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member)

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )

        project1 = Project(
            release=release,
            workflow=workflow,
            group=group,
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project1)

        issue1 = Issue(
            project=project1,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)

        cls.issue2 = Issue(
            project=project1,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2,
            room_id=3
        )
        session.add(cls.issue2)
        session.commit()

    def test_update(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Update a issue',
            f'/apiv1/issues/id:{self.issue2.id}',
            'UPDATE',
            form=dict(
                title='New issue',
                description='This is a description for new issue',
                dueDate='2200-12-12',
                kind='feature',
                days=4,
                priority='high',
                projectId=2
            )
        ):
            assert status == 200
            assert response.json['id'] == self.issue2.id
            assert response.json['priority'] == 'high'
            assert response.json['tags'] is not None

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Title is the same of it already is',
                form=given | dict(title='Another issue')
            )
            assert status == 200

            when(
                'Title is repetitive',
                form=given | dict(title='First issue')
            )
            assert status == '600 Another issue with title: "First issue" '\
                'is already exists.'

            when(
                'Title format is wrong',
                form=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

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
                'Invalid kind value is in form',
                form=given | dict(kind='enhancing', title='Another title')
            )
            assert status == '717 Invalid kind, only one of "feature, '\
                'bug" will be accepted'

            when(
                'Invalid status value is in form',
                form=given + dict(status='progressing') | \
                    dict(title='Another title')
            )
            assert status == '705 Invalid status, only one of "in-progress, '\
                'on-hold, to-do, done, complete" will be accepted'
            assert status.text.startswith('Invalid status')

            when(
                'Invalid priority value is in form',
                form=Update(priority='no_priority')
            )
            assert status == '767 Invalid priority, only one of "low, '\
                'normal, high" will be accepted'


            when(
                'Invalid parameter is in the form',
                form=given + dict(invalid_param='External parameter') | \
                    dict(title='Another title')
            )
            assert status == \
                '707 Invalid field, only following fields are accepted: '\
                'title, days, dueDate, kind, description, status, priority'

            when('Request is not authorized', authorization=None)
            assert status == 401

            when('Updating project with empty form', form=dict())
            assert status == '708 No Parameter Exists In The Form'

