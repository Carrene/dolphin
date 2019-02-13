from auditing.context import Context as AuditLogContext
from bddrest import status, when, given, response

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

        cls.project1 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(cls.project1)

        cls.project2 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My second project',
            description='A decription for my project',
            room_id=2
        )
        session.add(cls.project2)

        cls.project3 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My third project',
            description='A decription for my project',
            room_id=3
        )
        cls.project3.soft_delete()
        session.add(cls.project3)

        cls.issue1 = Issue(
            project=cls.project1,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)
        session.commit()

    def test_move(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            f'Move a issue',
            f'/apiv1/issues/id: {self.issue1.id}',
            f'MOVE',
            form=dict(
                projectId=self.project2.id,
            )
        ):
            assert status == 200
            assert response.json['id'] == self.issue1.id
            assert response.json['projectId'] == self.project2.id

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Not integer'),
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=0),
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                form=dict(projectId='Not integer'),
            )
            assert status == '714 Invalid Project Id Type'

            when(
                'Intended project with integer type not found',
                form=dict(projectId=0),
            )
            assert status == '601 Project not found with id: 0'

            when(
                'Trying to pass with hidden project',
                form=dict(projectId=self.project3.id),
            )
            assert status == '746 Hidden Project Is Not Editable'

            when(
                'Trying to pass without project id',
                form=given - 'projectId' + dict(a='a'),
            )
            assert status == '713 Project Id Not In Form'

            when('Request is not authorized', authorization=None)
            assert status == 401

            when('Updating project with empty form', form=dict())
            assert status == '708 No Parameter Exists In The Form'

