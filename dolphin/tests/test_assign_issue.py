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

        workflow1 = Workflow(title='First Workflow')

        project = Project(
            member=member,
            workflow=workflow1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        phase = Phase(
            title='development',
            order=2,
            workflow=workflow1
        )
        session.add(phase)

        resource = Resource(
            title='First Resource',
            email='resource1@example.com',
            access_token='access token 2',
            phone=987654321,
            reference_id=2
        )
        session.add(resource)

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
            form=dict(resourceId=2, phaseId=1)
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
                'Resource not found',
                form=given | dict(resourceId=100)
            )
            assert status == 609
            assert status.text.startswith('Resource not found')

            when(
                'Resource id is not in form',
                form=given - 'resourceId'
            )
            assert status == '715 Resource Id Not In Form'

            when(
                'Resource id type is not valid',
                form=given | dict(resourceId='Alphabetical')
            )
            assert status == '716 Invalid Resource Id Type'

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
                form=given | dict(resourceId=2)
            )
            assert status == '602 Already Assigned'

            when('Request is not authorized', authorization=None)
            assert status == 401

