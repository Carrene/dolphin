from auditor.context import Context as AuditLogContext
from bddrest import status, when, response, Remove, Update, given
from nanohttp import context
from nanohttp.contexts import Context
from sqlalchemy import func

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Issue, Project, Member, Phase, Group, Workflow, \
    Release, Specialty, Subscription, Item, IssuePhase, Skill


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext({})
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member1)
        session.commit()

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123456788,
            reference_id=2
        )
        session.add(cls.member2)

        cls.member3 = Member(
            title='Third Member',
            email='member3@example.com',
            access_token='access token 3',
            reference_id=3
        )
        session.add(cls.member3)

        workflow = Workflow(title='Default')
        session.add(workflow)

        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
        )
        cls.phase1 = Phase(
            title='design',
            order=1,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(cls.phase1)

        cls.phase2 = Phase(
            title='developement',
            order=2,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(cls.phase2)

        cls.phase3 = Phase(
            title='test',
            order=3,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(cls.phase3)

        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=group,
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        with Context(dict()):
            context.identity = cls.member1

            cls.issue1 = Issue(
                project=cls.project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)
            session.commit()

    def test_assign(self):
        self.login(self.member1.email)
        session = self.create_session()
        form = dict(
            memberId=self.member2.id,
            phaseId=self.phase2.id,
            description='A description for item',
            stage='triage'
        )

        with oauth_mockup_server(), self.given(
            'Assign an issue to a resource',
            f'/apiv1/issues/id: {self.issue1.id}',
            'ASSIGN',
            form=form
        ):
            assert status == 200
            assert response.json['id'] == self.issue1.id
            assert session.query(Subscription) \
                .filter(
                    Subscription.subscribable_id==self.issue1.id,
                    Subscription.member_id==self.member2.id
                ).one()

            assert session.query(Item) \
                .join(IssuePhase, IssuePhase.id == Item.issue_phase_id) \
                .filter(IssuePhase.issue_id == self.issue1.id) \
                .filter(IssuePhase.phase_id == form['phaseId']) \
                .filter(Item.member_id == form['memberId']) \
                .filter(Item.need_estimate_timestamp != None) \
                .one()

            when(
                'The issue already has a need estimate phase and we are '
                'assiging another member to issue on need estimate phase',
                form=given | dict(memberId=self.member3.id)
            )
            assert status == 200
            assert session.query(Item) \
                .join(IssuePhase, IssuePhase.id == Item.issue_phase_id) \
                .filter(IssuePhase.issue_id == self.issue1.id) \
                .filter(IssuePhase.phase_id == form['phaseId']) \
                .filter(Item.member_id == self.member3.id) \
                .filter(Item.need_estimate_timestamp != None) \
                .one()

            when(
                'The issue is assigned on phase with less order than issue '
                'need estimate phase',
                form=given | dict(phaseId=self.phase1.id)

            )
            assert status == 200
            assert session.query(Item) \
                .join(IssuePhase, IssuePhase.id == Item.issue_phase_id) \
                .filter(IssuePhase.issue_id == self.issue1.id) \
                .filter(IssuePhase.phase_id == self.phase1.id) \
                .filter(Item.member_id == form['memberId']) \
                .filter(Item.need_estimate_timestamp != None) \
                .one()
            assert session.query(func.count(Item.id)) \
                .join(IssuePhase, IssuePhase.id == Item.issue_phase_id) \
                .filter(IssuePhase.issue_id == self.issue1.id) \
                .filter(IssuePhase.phase_id == self.phase2.id) \
                .filter(Item.need_estimate_timestamp == None) \
                .scalar() == 2

            when(
                'There is invalid parameter in the form',
                form=given | dict(parameter='invalid parameter')
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: stage, isDone, description, phaseId, memberId, ' \
                'projectId, title, days, priority, kind, batch'

            when(
                'Stage value is wron',
                form=given | dict(stage='invalid value')
            )
            assert status == 705
            assert status.text.startswith('Invalid stage value')

            when(
                'Description is more than limit',
                form=given | dict(description=(512 + 1) * 'a')
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=0),
            )
            assert status == 404

            when('Member not found', form=Update(memberId=0))
            assert status == '609 Resource not found with id: 0'

            when(
                'Member id is not in form',
                form=Remove('memberId'),
            )
            assert len(response.json['items']) == 4

            when(
                'Member id type is not valid',
                form=Update(memberId='Alphabetical'),
            )
            assert status == '716 Invalid Resource Id Type'

            when('Phase not found', form=Update(phaseId=0))
            assert status == '613 Phase Not Found'

            when('Phase id is not in form', form=Remove('phaseId'))
            assert status == '737 Phase Id Not In Form'

            when(
                'Phase id type is not valid',
                form=Update(phaseId='Alphabetical')
            )
            assert status == '738 Invalid Phase Id Type'

            when(
                'Issue is already assigned',
                url_parameters=dict(id=self.issue1.id),
            )
            assert status == '602 Already Assigned'

            when('Request is not authorized', authorization=None)
            assert status == 401

