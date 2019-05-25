from auditor.context import Context as AuditLogContext
from bddrest import status, response, when

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Member, Workflow, Group, Project, Issue, Release


class TestDraftIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)

        workflow = Workflow(title='default')

        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        cls.issue = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue)
        session.commit()

    def test_define(self):
        self.login(self.member.email, self.member.password)

        with self.given(
            'Define a draft issue',
            '/apiv1/draftissues',
            'DEFINE',
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['issueId'] is None

            when(
                'Trying to pass with invalid form parameres',
                form=dict(a='a'),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, kind, days, status, projectId,' \
                ' dueDate, priority, relatedIssueId'

            when('Request is not authorized', authorization=None)
            assert status == 401

