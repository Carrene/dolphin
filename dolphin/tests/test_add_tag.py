from bddrest import status, response, when, Update

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Tag, DraftIssue, Issue, Organization, \
    OrganizationMember, Project


class TestTag(LocalApplicationTestCase):

    @classmethod
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

        organization_member = OrganizationMember(
            organization_id=organization.id,
            member_id=cls.member1.id,
            role='owner',
        )
        session.add(organization_member)

        cls.tag = Tag(
            title='tag 1',
            organization_id=organization.id,
        )
        session.add(cls.tag)

        cls.draft_issue = DraftIssue()
        session.add(cls.draft_issue)

        project = Project(
            member=cls.member1,
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
        session.commit()

    def test_add_tag_to_draft_issue(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            f'Adding a tag to the draft issue',
            f'/apiv1/draftissues/draft_issue_id: {self.draft_issue.id}'
                f'/tags/id: {self.tag.id}',
            f'ADD',
        ):
            assert status == 200
            assert response.json['id'] == self.tag.id

            when('Trying to pass with form parameters', form=dict(a='a'))
            assert status == '709 Form Not Allowed'

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

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_add_tag_to_issue(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            f'Adding a tag to the draft issue',
            f'/apiv1/issues/issue_id: {self.issue.id}/tags/id: {self.tag.id}',
            f'ADD',
        ):
            assert status == 200
            assert response.json['id'] == self.tag.id

            when('Trying to pass with form parameters', form=dict(a='a'))
            assert status == '709 Form Not Allowed'

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

            when('Request is not authorized', authorization=None)
            assert status == 401

