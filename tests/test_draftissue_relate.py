from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from nanohttp import context
from nanohttp.contexts import Context

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Issue, Member, Workflow, Group, Project, Release, \
    DraftIssue, DraftIssueIssue


class TestDraftIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(cls.member)
        session.commit()

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
            room_id=1,
        )

        with Context(dict()):
            context.identity = cls.member

            cls.draft_issue = DraftIssue()
            session.add(cls.draft_issue)

            cls.issue1 = Issue(
                project=project,
                title='Second issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2,
            )
            session.add(cls.issue1)
            session.commit()

    def test_relate(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Getting a issue',
            f'/apiv1/draftissues/id:{self.draft_issue.id}',
            f'RELATE',
            json=dict(targetIssueId=self.issue1.id)
        ):
            assert status == 200
            assert response.json['id'] == self.draft_issue.id

            session = self.create_session()
            draftissue_issue = session.query(DraftIssueIssue) \
                .filter(DraftIssueIssue.draft_issue_id == self.draft_issue.id) \
                .count()
            assert draftissue_issue == 1

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='not-integer')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Issue already is related',
            )
            assert status == '645 Already Is Related'

            when(
                'Trying to pass with not exist issue',
                json=dict(targetIssueId=0)
            )
            assert status == '648 Target Issue Not Found'

            when(
                'Trying to pass with none issue id',
                json=dict(targetIssueId=None)
            )
            assert status == '779 Target Issue Id Is Null'

            when(
                'Trying to pass with invalid issue id type',
                json=dict(targetIssueId='id')
            )
            assert status == '781 Invalid Target Issue Id Type'

            when('Form parameter is sent with request', json={})
            assert status == '708 Empty Form'

            when('Request is not authorized', authorization=None)
            assert status == 401

