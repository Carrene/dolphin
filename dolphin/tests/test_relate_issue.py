from auditing.context import Context as AuditLogContext
from bddrest import status, response, when, Update

from dolphin.models import Issue, Member, Workflow, Group, Project, Release, \
    RelatedIssue
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member)

        workflow = Workflow(title='default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            member=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        cls.issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)

        cls.issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue2)

        cls.issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue3)
        session.flush()

        related_issue = RelatedIssue(
            issue_id=cls.issue1.id,
            related_issue_id=cls.issue3.id
        )
        session.add(related_issue)
        session.commit()

    def test_relate(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Getting a issue',
            f'/apiv1/issues/id:{self.issue1.id}',
            f'RELATE',
            json=dict(issueId=self.issue2.id)
        ):
            import pudb; pudb.set_trace()  # XXX BREAKPOINT
            assert status == 200
            assert response.json['id'] == self.issue1.id

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Issue already is related',
                json=dict(issueId=self.issue3.id)
            )
            assert status == '645 Already Is Related'

            when(
                'Trying to pass with not exist issue',
                json=dict(issueId=0)
            )
            assert status == '605 Issue Not Found'

            when(
                'Trying to pass with none issue id',
                json=dict(issueId=None)
            )
            assert status == '775 Issue Id Is None'

            when(
                'Trying to pass with invalid issue id type',
                json=dict(issueId='id')
            )
            assert status == '722 Invalid Issue Id type'

            when('Form parameter is sent with request', json={})
            assert status == '708 Empty Form'

            when('Request is not authorized', authorization=None)
            assert status == 401

