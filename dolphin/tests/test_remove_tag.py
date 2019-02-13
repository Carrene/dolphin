from auditing.context import Context as AuditLogContext
from bddrest import status, response, when, Update

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Tag, DraftIssue, Issue, Organization, \
    OrganizationMember, Project, DraftIssueTag, IssueTag, Workflow, Group, \
    Release


class TestTag(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member1)
        organization = Organization(
            title='organization-title',
        )
        session.add(organization)
        session.flush()

        workflow = Workflow(title='Default')
        group = Group(title='default')

        organization_member = OrganizationMember(
            organization_id=organization.id,
            member_id=cls.member1.id,
            role='owner',
        )
        session.add(organization_member)

        cls.tag1 = Tag(
            title='tag 1',
            organization_id=organization.id,
        )
        session.add(cls.tag1)

        cls.tag2 = Tag(
            title='tag 2',
            organization_id=organization.id,
        )
        session.add(cls.tag2)

        cls.draft_issue = DraftIssue()
        session.add(cls.draft_issue)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

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

        session.flush()
        draft_issue_tag = DraftIssueTag(
            draft_issue_id=cls.draft_issue.id,
            tag_id=cls.tag1.id
        )
        session.add(draft_issue_tag)

        issue_tag = IssueTag(
            issue_id=cls.issue.id,
            tag_id=cls.tag1.id,
        )
        session.add(issue_tag)
        session.commit()

    def test_remove_tag_to_draft_issue(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            f'Removing a tag to the draft issue',
            f'/apiv1/draftissues/draft_issue_id: {self.draft_issue.id}'
                f'/tags/id: {self.tag1.id}',
            f'REMOVE',
        ):
            assert status == 200
            assert response.json['id'] == self.tag1.id

            when(
                'Already tag is removed',
                url_parameters=Update(id=self.tag2.id)
            )
            assert status == '635 Already Tag Removed'

            ## FIXME Uncomment aftre fixing bug in jsonpatch
            #when('Trying to pass with form parameters', form=dict(a='a'))
            #assert status == '709 Form Not Allowed'

            when(
                'Trying to pass with wrong draft issue id',
                url_parameters=Update(draft_issue_id=0)
            )
            assert status == 404

            when(
                'Trying to pass with wrong tag id',
                 url_parameters=Update(id=0)
            )
            assert status == 404

            when(
                'Type of tag id is invalid',
                url_parameters=Update(id='not-integer')
            )
            assert status == 404

            when(
                'Type of draft issue id is invalid',
                url_parameters=Update(draft_issue_id='not-integer')
            )
            assert status == 404

            when(
                'Trying to pass without draft issue',
                url=f'/apiv1/tags/{self.tag1.id}'
            )
            assert status == 403

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_remove_tag_to_issue(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            f'Adding a tag to the draft issue',
            f'/apiv1/issues/issue_id: {self.issue.id}/tags/id: {self.tag1.id}',
            f'REMOVE',
        ):
            assert status == 200
            assert response.json['id'] == self.tag1.id

            when(
                'Already tag is removed',
                url_parameters=Update(id=self.tag2.id)
            )
            assert status == '635 Already Tag Removed'

            ## FIXME Uncomment aftre fixing bug in jsonpatch
            #when('Trying to pass with form parameters', form=dict(a='a'))
            #assert status == '709 Form Not Allowed'

            when(
                'Trying to pass with wrong issue id',
                url_parameters=Update(issue_id=0)
            )
            assert status == 404

            when(
                'Trying to pass with wrong tag id',
                 url_parameters=Update(id=0)
            )
            assert status == 404

            when(
                'Type of tag id is invalid',
                url_parameters=Update(id='not-integer')
            )
            assert status == 404

            when(
                'Type of draft issue id is invalid',
                url_parameters=Update(issue_id='not-integer')
            )
            assert status == 404

            when(
                'Trying to pass without issue',
                url=f'/apiv1/tags/{self.tag1.id}'
            )
            assert status == 403

            when('Request is not authorized', authorization=None)
            assert status == 401

