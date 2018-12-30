from bddrest import status, when, given, response

from dolphin.models import Issue, Project, Member, Phase, Resource, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )

        workflow = Workflow(title='default')
        session.add(workflow)

        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow
        )
        session.add(phase1)

        phase2 = Phase(
            title='triage',
            order=0,
            workflow=workflow
        )
        session.add(phase2)

        project = Project(
            workflow=workflow,
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)
        session.commit()
        cls.project = project

    def test_assign(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Assign an issue to a resource',
            '/apiv1/issues/id:2',
            'ASSIGN',
            form=dict(memberId=1, phaseId=1)
        ):
            assert status == 200
            assert response.json['id'] == 2

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Member not found',
                form=given | dict(memberId=100)
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member id is not in form',
                form=given - 'memberId'
            )
            assert status == '735 Member Id Not In Form'

            when(
                'Member id type is not valid',
                form=given | dict(memberId='Alphabetical')
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'Phase not found',
                form=given | dict(phaseId=100)
            )
            assert status == 613
            assert status.text.startswith('Phase not found')

            when(
                'Phase id is not in form',
                form=given - 'phaseId'
            )
            assert status == '737 Phase Id Not In Form'

            when(
                'Phase id type is not valid',
                form=given | dict(phaseId='Alphabetical')
            )
            assert status == '738 Invalid Phase Id Type'

            when(
                'Issue is already assigned',
                url_parameters=dict(id=2),
                form=given | dict(resourceId=1)
            )
            assert status == '602 Already Assigned'

            when('Request is not authorized', authorization=None)
            assert status == 401

