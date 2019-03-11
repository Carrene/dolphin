from bddrest import status, response, when, Remove, given, Update

from dolphin.models import Project, Member, Workflow, Release, Group
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestProject(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            manager=cls.member,
        )

        cls.workflow = Workflow(title='Default')
        cls.group = Group(title='Public', public=True)

        project1 = Project(
            workflow=cls.workflow,
            group=cls.group,
            release=release1,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)
        session.commit()


    def test_create(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Createing a project',
            '/apiv1/projects',
            'CREATE',
            json=dict(
                workflowId=self.workflow.id,
                releaseId=1,
                title='My awesome project',
                description='A decription for my project',
                status='active',
                managerReferenceId=self.member.reference_id,
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome project'
            assert response.json['description'] == 'A decription for my project'
            assert response.json['status'] == 'active'
            assert response.json['boarding'] == None
            assert response.json['dueDate'] == None
            assert response.json['managerId'] == self.member.id
            assert response.json['secondaryManagerId'] is None

            when(
                'Trying to create a project with secondary manager',
                json=Update(
                    title='project',
                    secondaryManagerReferenceId=self.member.reference_id
                )
            )
            assert response.json['secondaryManagerId'] == self.member.id

            when(
                'Secondary manager reference id is null',
                json=Update(
                    title='New Project',
                    secondaryManagerReferenceId=None
                )
            )
            assert status == '782 Secondary Manager Reference Id Is Null'

            when(
                'Secondary manager is not found',
                json=Update(
                    title='New Project',
                    secondaryManagerReferenceId=0
                )
            )
            assert status == '650 Secondary Manager Not Found'

            when(
                'Manager reference id is null',
                json=Update(title='New Project', managerReferenceId=None)
            )
            assert status == '778 Manager Reference Id Is Null'

            when(
                'Manager is not found',
                json=Update(title='New Project', managerReferenceId=0)
            )
            assert status == '608 Manager Not Found'

            when(
                'Maneger reference id is not in form',
                json=given - 'managerReferenceId' | dict(title='New Project')
            )
            assert status == '777 Manager Reference Id Not In Form'

            when(
                'Workflow id is not in form',
                json=given - 'workflowId' | dict(title='New Project')
            )
            assert status == 200

            when(
                'Workflow id is in form but not found(alphabetical)',
                json=given | dict(title='New title', workflowId='Alphabetical')
            )
            assert status == '743 Invalid Workflow Id Type'

            when(
                'Workflow id is in form but not found(numeric)',
                json=given | dict(title='New title', workflowId=0)
            )
            assert status == '616 Workflow not found with id: 0'

            when(
                'Title format is wrong',
                json=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title is repetetive',
                json=given | dict(title='My first project')
            )
            assert status == '600 Another project with title: My first '\
                'project is already exists.'

            when(
                'Release ID type is wrong',
                json=given | dict(releaseId='Alphabetical', title='New title')
            )
            assert status == '750 Invalid Release Id Type'

            when(
                'Release not found with integer type',
                json=given | dict(releaseId=0, title='New title')
            )
            assert status == '607 Release not found with id: 0'

            when(
                'Title is not in form',
                json=Remove('title')
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                json=given | dict(title=((128 + 1) * 'a'))
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                json=given | dict(
                    description=((8192 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At Most 8192 Characters Are Valid For '\
                'Description'

            when(
                'Status value is invalid',
                json=given | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == '705 Invalid status value, only one of "active, '\
                'on-hold, queued, done" will be accepted'

            when('Request is not authorized', authorization=None)
            assert status == 401

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

