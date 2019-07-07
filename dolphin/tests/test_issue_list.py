from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Issue, Project, Member, Workflow, Item, Phase, \
    Group, Subscription, Release, Skill, Organization, Tag, IssuePhase
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.organization = Organization(
            title='organization title',
        )
        session.add(cls.organization)
        session.flush()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member)
        session.commit()

        cls.tag1 = Tag(
            title='First tag',
            organization_id=cls.organization.id,
        )
        session.add(cls.tag1)
        session.flush()

        cls.tag2 = Tag(
            title='Second tag',
            organization_id=cls.organization.id,
        )
        session.add(cls.tag2)
        session.flush()

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member,
            room_id=0,
            group=group,
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = member

            cls.issue1 = Issue(
                project=cls.project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2,
                tags=[cls.tag1],
                stage='triage',
            )
            session.add(cls.issue1)
            session.flush()

            subscription_issue1 = Subscription(
                subscribable_id=cls.issue1.id,
                member_id=member.id,
                seen_at=datetime.utcnow(),
            )
            session.add(subscription_issue1)

            cls.issue2 = Issue(
                project=cls.project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=2,
                room_id=3,
                tags=[cls.tag2],
            )
            session.add(cls.issue2)
            session.flush()

            subscription_issue2 = Subscription(
                subscribable_id=cls.issue2.id,
                member_id=member.id,
                seen_at=None,
                one_shot=True,
            )
            session.add(subscription_issue2)

            cls.issue3 = Issue(
                project=cls.project,
                title='Third issue',
                description='This is description of third issue',
                kind='feature',
                stage='on-hold',
                days=3,
                room_id=4,
            )
            session.add(cls.issue3)
            session.flush()

            subscription_issue3 = Subscription(
                subscribable_id=cls.issue3.id,
                member_id=member.id,
                seen_at=None,
                one_shot=True,
            )
            session.add(subscription_issue3)

            cls.issue4 = Issue(
                project=cls.project,
                title='Fourth issue',
                description='This is description of fourth issue',
                kind='feature',
                days=3,
                room_id=4,
                tags=[cls.tag2],
            )
            session.add(cls.issue4)
            session.flush()

            cls.phase1 = Phase(
                workflow=workflow,
                title='Backlog',
                order=1,
                skill=skill,
            )
            session.add(cls.phase1)
            session.flush()

            cls.phase2 = Phase(
                workflow=workflow,
                title='Test',
                order=2,
                skill=skill
            )
            session.add(cls.phase1)
            session.flush()

            cls.phase3 = Phase(
                workflow=workflow,
                title='Development',
                order=3,
                skill=skill
            )
            session.add(cls.phase1)
            session.flush()

            issue_phase1 = IssuePhase(
                issue=cls.issue1,
                phase=cls.phase1,
            )

            item1 = Item(
                member_id=member.id,
                issue_phase=issue_phase1,
            )
            session.add(item1)
            session.flush()

            issue_phase2 = IssuePhase(
                issue=cls.issue2,
                phase=cls.phase2,
            )

            item2 = Item(
                member_id=member.id,
                issue_phase=issue_phase2,
            )
            session.add(item2)
            session.flush()

            issue_phase3 = IssuePhase(
                issue=cls.issue1,
                phase=cls.phase2,
            )

            item3 = Item(
                member_id=member.id,
                issue_phase=issue_phase3,
                start_date='2019-2-2',
                end_date='2019-2-3',
                estimated_hours=4,
            )
            session.add(item3)
            session.flush()

            issue_phase4 = IssuePhase(
                issue=cls.issue2,
                phase=cls.phase1,
            )

            item4 = Item(
                member_id=member.id,
                issue_phase=issue_phase4,
                start_date='2019-2-2',
                end_date='2019-2-3',
                estimated_hours=4,
            )
            session.add(item4)
            session.flush()

            issue_phase5 = IssuePhase(
                issue=cls.issue2,
                phase=cls.phase3,
            )

            item5 = Item(
                member_id=member.id,
                issue_phase=issue_phase5,
            )
            session.add(item5)
            session.flush()

            issue_phase6 = IssuePhase(
                issue=cls.issue3,
                phase=cls.phase1,
            )

            item6 = Item(
                member_id=member.id,
                issue_phase=issue_phase6,
            )
            session.add(item6)
            session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List issues',
            '/apiv1/issues',
            'LIST',
        ):
            assert status == 200

            issues = response.json
            assert len(issues) == 4

            for issue in issues:
                items = issue['items']
                if len(items) == 0:
                    continue

                privious_item_created_at = items[0]['createdAt']
                for item in items:
                    assert item['createdAt'] >= privious_item_created_at
                    privious_item_created_at = item['createdAt']

            when('Unread messages', query=dict(unread=True))
            assert len(response.json) == 2

            when('Sort issues by title', query=dict(sort='title'))
            assert response.json[0]['title'] == self.issue1.title
            assert response.json[1]['title'] == self.issue4.title
            assert response.json[2]['title'] == self.issue2.title
            assert response.json[3]['title'] == self.issue3.title

            when('Sort issues by status', query=dict(sort='status'))
            assert response.json[0]['status'] == 'to-do'
            assert response.json[1]['status'] == 'to-do'
            assert response.json[2]['status'] == 'to-do'
            assert response.json[3]['status'] == 'to-do'

            when('Filter by status', query=dict(status='to-do'))
            assert status == 200
            assert len(response.json) == 4

            when('Filter by response time', query=dict(responseTime=47))
            assert status == 200
            assert len(response.json) == 1

            when(
                'Filter by multi statuses',
                query=dict(status='IN(to-do, in-progress)')
            )
            assert status == 200
            assert len(response.json) == 4

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == self.issue3.title
            assert response.json[1]['title'] == self.issue2.title
            assert response.json[2]['title'] == self.issue4.title
            assert response.json[3]['title'] == self.issue1.title

            when('Filter issues', query=dict(title='First issue'))
            assert response.json[0]['title'] == 'First issue'

            when(
                'List issues except one of them',
                query=dict(title='!Second issue')
            )
            assert len(response.json) == 3

            when(
                'Filter based on a hybrid property',
                query=dict(boarding='delayed')
            )
            assert len(response.json) == 2

            when(
                'Filter based on a stage',
                query=dict(stage='on-hold')
            )
            assert len(response.json) == 1
            assert response.json[0]['boarding'] == 'frozen'

            when('Issues pagination', query=dict(take=1, skip=2))
            assert response.json[0]['title'] == 'Third issue'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == self.issue4.title

            when('Filter by phase id', query=dict(phaseId=self.phase2.id))
            assert status == 200
            assert len(response.json) == 1

            when(
                'Filter by phase id with IN function',
                query=dict(phaseId=f'IN({self.phase1.id}, {self.phase2.id})')
            )
            assert len(response.json) == 2

            when(
                'Filtering the issues by phase title',
                query=dict(phaseTitle=self.phase1.title)
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue2.id


            when(
                'Filtering and sorting the issues by phase title',
                query=dict(phaseTitle=self.phase1.title, sort='phaseId')
            )
            assert len(response.json) == 1

            when(
                'Filtering the issues by phase title and phase id',
                query=dict(
                    phaseTitle=self.phase2.title,
                    phaseId=self.phase2.id
                )
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue1.id

            when(
                'Filtering the issues by tag id',
                query=dict(tagId=self.tag1.id)
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue1.id
            assert response.json[0]['title'] == self.issue1.title

            when(
                'Filtering the issues by tag title',
                query=dict(tagTitle=self.tag1.title)
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue1.id
            assert response.json[0]['title'] == self.issue1.title

            when(
                'Filtering the issues by tag title and tag id',
                query=dict(
                    tagTitle=self.tag1.title,
                    tagId=self.tag1.id
                )
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue1.id
            assert response.json[0]['title'] == self.issue1.title

            when(
                'Filter by phase id with IN function',
                query=dict(
                    projectId=self.project.id,
                    phaseId=f'IN({self.phase1.id})',
                    sort='createdAt',
                )
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue2.id

            when('Sort by phase id', query=dict(sort='phaseId'))
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue2.id

            when('Reverse sort by phase id', query=dict(sort='-phaseId'))
            assert status == 200
            assert len(response.json) == 4
            assert response.json[3]['id'] == self.issue2.id

            when('Sort by tag id', query=dict(sort='tagId'))
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue1.id
            assert response.json[1]['id'] == self.issue2.id
            assert response.json[2]['id'] == self.issue4.id
            assert response.json[3]['id'] == self.issue3.id

            when('Reverse sort by tag id', query=dict(sort='-tagId'))
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue3.id
            assert response.json[1]['id'] == self.issue2.id
            assert response.json[2]['id'] == self.issue4.id
            assert response.json[3]['id'] == self.issue1.id

            when('Sort by tag id and title', query=dict(sort='tagId,title'))
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue1.id
            assert response.json[1]['id'] == self.issue4.id

            when(
                'Sort by tag id and reverse title',
                query=dict(sort='tagId,-title')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue1.id
            assert response.json[1]['id'] == self.issue2.id

            when(
                'Sort and filter by phase id at the same time',
                query=dict(sort='phaseId', phaseId=self.phase1.id)
            )
            assert status == 200
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue2.id

            when(
                'Sort and filter by tag id at the same time',
                query=dict(sort='tagId', tagId=self.tag2.id)
            )
            assert status == 200
            assert len(response.json) == 2
            assert response.json[0]['id'] == self.issue2.id
            assert response.json[1]['id'] == self.issue4.id

            when(
                'Sort issues by tag title',
                query=dict(sort='tagTitle')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue1.id
            assert response.json[1]['id'] == self.issue2.id
            assert response.json[2]['id'] == self.issue4.id
            assert response.json[3]['id'] == self.issue3.id

            when(
                'Reverse sort issues by tag title',
                query=dict(sort='-tagTitle')
            )
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue3.id
            assert response.json[1]['id'] == self.issue2.id
            assert response.json[2]['id'] == self.issue4.id
            assert response.json[3]['id'] == self.issue1.id

            when('Sort by phase title', query=dict(sort='phaseTitle'))
            assert status == 200
            assert len(response.json) == 4
            assert response.json[0]['id'] == self.issue2.id
            assert response.json[1]['id'] == self.issue1.id

            when('Reverse sort by phase title', query=dict(sort='-phaseTitle'))
            assert status == 200
            assert len(response.json) == 4
            assert response.json[3]['id'] == self.issue2.id
            assert response.json[2]['id'] == self.issue1.id

            when(
                'Filter by phase id and sort by phase title',
                query=dict(sort='phaseTitle', phaseId=1)
            )
            assert status == 200
            assert len(response.json) == 1

            when(
                'filter by triage phase id',
                query=dict(phaseId='IN(0,1)')
            )
            assert len(response.json) == 3

            when('Request is not authorized', authorization=None)
            assert status == 401

