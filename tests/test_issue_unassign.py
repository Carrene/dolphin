from auditor.context import Context as AuditLogContext
from bddrest import status, when, response, Update, Remove
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Issue, Project, Member, Phase, Group, Workflow, \
    Item, Release, Skill, IssuePhase
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext({})
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member)
        session.commit()

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')

        cls.phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase1)

        group = Group(title='Default')

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

        with Context(dict()):
            context.identity = cls.member

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue2)
            session.flush()

            issue_phase1 = IssuePhase(
                issue=cls.issue1,
                phase=cls.phase1,
            )

            item = Item(
                issue_phase=issue_phase1,
                member_id=cls.member.id,
            )
            session.add(item)
            session.commit()

    def test_unassign(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'UNAssign an issue from a resource',
            f'/apiv1/issues/id: {self.issue1.id}',
            f'UNASSIGN',
            form=dict(memberId=self.member.id, phaseId=self.phase1.id)
        ):
            assert status == 200
            assert response.json['id'] == self.issue1.id

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='not-integer'),
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=0),
            )
            assert status == 404

            when('Resource not found', form=Update(memberId=0))
            assert status == '609 Resource not found with id: 0'

            when(
                'Trying to pass without resource id',
                form=Remove('memberId')
            )
            assert status == '715 Resource Id Not In Form'

            when(
                'Member id type is not valid',
                form=Update(memberId='not-integer')
            )
            assert status == '716 Invalid Resource Id Type'

            when(
                'Intended phase with integer type not found',
                form=Update(phaseId=0)
            )
            assert status == '613 Phase Not Found'

            when('Phase id is not in form', form=Remove('phaseId'))
            assert status == '737 Phase Id Not In Form'

            when(
                'Phase id type is not valid',
                form=Update(phaseId='not-integer')
            )
            assert status == '738 Invalid Phase Id Type'

            when(
                'Issue not assigned yet',
                url_parameters=dict(id=self.issue2.id)
            )
            assert status == '636 Not Assigned Yet'

            when('Request is not authorized', authorization=None)
            assert status == 401

