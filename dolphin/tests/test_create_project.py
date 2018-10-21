from bddrest import status, response, when, Remove, given

from dolphin.models import Project, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestProject(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )

        workflow1 = Workflow(title='First Workflow')

        project1 = Project(
            member=member1,
            workflow=workflow1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)
        session.commit()
        cls.member = member1
        cls.workflow = workflow1

    def test_create(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Createing a project',
            '/apiv1/projects',
            'CREATE',
            form=dict(
                memberId=self.member.id,
                workflowId=self.workflow.id,
                title='My awesome project',
                description='A decription for my project',
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome project'
            assert response.json['description'] == 'A decription for my project'
            assert response.json['status'] == 'queued'
            assert response.json['boarding'] == None
            assert response.json['dueDate'] == None

            when(
                'Member id not in form',
                form=given - 'memberId' | dict(title='New title')
            )
            assert status == '739 Member Id Not In Form'

            when(
                'Member not found with string type',
                form=given | dict(memberId='Alphabetical', title='New title')
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member not found with integer type',
                form=given | dict(memberId=100, title='New title')
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Title format is wrong',
                form=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title is repetetive',
                form=given | dict(title='My first project')
            )
            assert status == 600
            assert status.text.startswith('Another project with title')

            when(
                'Release not found with string type',
                form=given | dict(releaseId='Alphabetical', title='New title')
            )
            assert status == 607
            assert status.text.startswith('Release not found')

            when(
                'Release not found with integer type',
                form=given | dict(releaseId=100, title='New title')
            )
            assert status == 607
            assert status.text.startswith('Release not found')

            when(
                'Title is not in form',
                form=Remove('title')
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For '\
                'Description'

            when(
                'Status value is invalid',
                form=given | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when('Request is not authorized', authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    form=given | dict(title='Another title')
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    form=given | dict(title='Another title')
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(title='Another title')
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('615 Room Already Exists'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(title='Another title')
                )
                assert status == 200

            with chat_server_status('604 Already Added To Target'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(title='Awesome project')
                )
                assert status == 200

