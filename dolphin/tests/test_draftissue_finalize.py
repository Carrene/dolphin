from nanohttp.contexts import Context
from nanohttp import context
from auditor import MiddleWare
from auditor.context import Context as AuditLogContext
from auditor.logentry import RequestLogEntry, InstantiationLogEntry
from bddrest import status, response, Update, when, given, Remove

from dolphin import Dolphin
from dolphin.middleware_callback import callback as auditor_callback
from dolphin.models import Issue, Project, Workflow, Phase, Tag, \
    DraftIssue, Organization, OrganizationMember, Group, Release, Skill, Resource
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


def callback(audit_logs):
    global logs
    logs = audit_logs
    auditor_callback(audit_logs)


class TestIssue(LocalApplicationTestCase):
    __application__ = MiddleWare(Dolphin(), callback)

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        skill = Skill(title='Project Manager')

        cls.member = Resource(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
            skill=skill,
        )

        workflow1 = Workflow(title='default')

        phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow1,
            skill=skill,
        )
        session.add(phase1)

        phase2 = Phase(
            title='Triage',
            order=0,
            workflow=workflow1,
            skill=skill,
        )
        session.add(phase2)

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

        cls.project = Project(
            release=release,
            workflow=workflow1,
            group=group,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = cls.member

            cls.issue1 = Issue(
                project=cls.project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)

            cls.draft_issue1 = DraftIssue()
            session.add(cls.draft_issue1)

            organization = Organization(
                title='organization-title',
            )
            session.add(organization)
            session.flush()

            cls.draft_issue1.related_issues = [cls.issue1]

            organization_member = OrganizationMember(
                organization_id=organization.id,
                member_id=cls.member.id,
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

            cls.tag3 = Tag(
                title='tag 3',
                organization_id=organization.id,
            )
            session.add(cls.tag3)

            cls.draft_issue1.tags = [cls.tag1, cls.tag2]

            cls.draft_issue2 = DraftIssue()
            session.add(cls.draft_issue2)
            session.commit()

    def test_finalize(self):
        self.login(self.member.email)
        session = self.create_session()

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            f'Define an issue',
            f'/apiv1/draftissues/id: {self.draft_issue1.id}',
            f'FINALIZE',
            json=dict(
                title='Defined issue',
                status='in-progress',
                description='A description for defined issue',
                kind='feature',
                days=3,
                projectId=self.project.id,
                priority='high',
            )
        ):
            assert status == 200
            assert response.json['id'] == self.draft_issue1.id
            assert response.json['issueId'] is not None
            assert len(response.json['tags']) == 2

            created_issue_id = response.json['issueId']
            created_issue = session.query(Issue).get(created_issue_id)
            assert created_issue.modified_by is None

            assert len(logs) == 2
            assert isinstance(logs[0], InstantiationLogEntry)
            assert isinstance(logs[1], RequestLogEntry)

            when(
                'Status is null',
                json=given | dict(status=None, title='new title')
            )
            assert status == 200

            when('Priority value not in form', json=Remove('priority'))
            assert status == '768 Priority Not In Form'

            when('Invalid the priority value', json=Update(priority='lorem'))
            assert status == '767 Invalid priority, only one of "low, '\
                'normal, high" will be accepted'

            when(
                'Draft issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                json=given | dict(title='New title')
            )
            assert status == 404

            when(
                'Draft issue not found',
                url_parameters=dict(id=0),
                json=given | dict(title='New title')
            )
            assert status == 404

            when(
                'Project id not in form',
                json=given - 'projectId' | dict(title='New title')
            )
            assert status == '713 Project Id Not In Form'

            when(
                'Project not found with string type',
                json=given | dict(projectId='Alphabetical', title='New title')
            )
            assert status == '714 Invalid Project Id Type'

            when(
                'Project not found with integer type',
                json=given | dict(projectId=0, title='New title')
            )
            assert status == '601 Project Not Found'

            when(
                'Relate issue not found with string type',
                json=Update(relatedIssueId='Alphabetical', title='New title')
            )
            assert status == '722 Invalid Issue Id Type'

            when(
                'Relate to issue not found with integer type',
                json=Update(relatedIssueId=0, title='New title')
            )
            assert status == 647
            assert status.text.startswith('relatedIssue With Id')

            when(
                'Include related issue',
                json=Update(relatedIssueId=self.issue1.id, title='New title')
            )
            assert status == 200

            when(
                'Title is not in form',
                json=given - 'title'
            )
            assert status == '710 Title Not In Form'

            when(
                'Title format is wrong',
                json=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title is repetitive',
                json=Update(title='First issue')
            )
            assert status == '600 Repetitive Title'

            when(
                'Title length is more than limit',
                json=given | dict(title=((128 + 1) * 'a'))
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                json=given | dict(
                    description=((8192 + 1) * 'a'),
                    title=('Another title')
                )
            )
            assert status == '703 At Most 8192 Characters Are Valid For '\
                'Description'

            when(
                'Kind is not in form',
                json=given - 'kind' | dict(title='Another title')
            )
            assert status == '718 Kind Not In Form'

            when(
                'Days is not in form',
                json=given - 'days' | dict(title='Another title')
            )
            assert status == '720 Days Not In Form'

            when(
                'Days type is wrong',
                json=given | dict(
                    days='Alphabetical',
                    title='Another title'
                )
            )
            assert status == '721 Invalid Days Type'

            when(
                'Invalid kind value is in form',
                json=given | dict(kind='enhancing', title='Another title')
            )
            assert status == '717 Invalid kind, only one of "feature, bug" '\
                'will be accepted'

            when(
                'Invalid status value is in form',
                json=given | dict(status='progressing') | \
                    dict(title='Another title')
            )
            assert status == '705 Invalid status value, only one of "to-do, ' \
                'in-progress, on-hold, complete, done" will be accepted'

            when(
                'Trying to pass with invalid form parameters',
                json=Update(a=1)
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, kind, days, status, projectId, ' \
                'priority, relatedIssueId'

            when('Request is not authorized', authorization=None)
            assert status == 401

            when(
                'Trying to pass draft issue bug without related issue',
                url_parameters=dict(id=self.draft_issue2.id),
                json=Update(
                    title='Another title',
                    kind='bug'
                )
            )
            assert status == '649 The Issue Bug Must Have A Related Issue'

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    json=given | dict(title='Another title')
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    json=given | dict(title='Another title')
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    json=given | dict(title='Another title')
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('615 Room Already Exists'):
                when(
                    'Chat server faces with internal error',
                    json=given | dict(title='Another title')
                )
                assert status == 200

            with chat_server_status('604 Already Added To Target'):
                when(
                    'Chat server faces with internal error',
                    json=given | dict(title='Awesome project')
                )
                assert status == 200

