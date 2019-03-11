from auditor.context import Context as AuditLogContext
from bddrest import status, when, response, Remove, Update

from dolphin.models import Issue, Project, Member, Phase, Group, Workflow, \
    Release, Skill
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


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

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123456788,
            reference_id=2
        )
        session.add(cls.member2)

        workflow = Workflow(title='Default')
        session.add(workflow)

        skill = Skill(title='First Skill')
        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase1)

        phase2 = Phase(
            title='triage',
            order=0,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase2)

        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
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

        cls.issue1 = Issue(
            project=cls.project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)
        session.commit()

    def test_assign(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'Assign an issue to a resource',
            f'/apiv1/issues/id:{self.issue1.id}',
            'ASSIGN',
            form=dict(memberId=self.member2.id, phaseId=1)
        ):
            assert status == 200
            assert response.json['id'] == self.issue1.id

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
            assert len(response.json['items']) == 2

            when(
                'Member id type is not valid',
                form=Update(memberId='Alphabetical'),
            )
            assert status == '716 Invalid Resource Id Type'

            when('Phase not found', form=Update(phaseId=0))
            assert status == '613 Phase not found with id: 0'

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

