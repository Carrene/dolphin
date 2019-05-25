from datetime import datetime

from auditor import MiddleWare
from auditor.context import Context as AuditLogContext
from auditor.logentry import RequestLogEntry, InstantiationLogEntry
from bddrest import status, response, when, Remove, given, Update

from dolphin import Dolphin
from dolphin.middleware_callback import callback as auditor_callback
from dolphin.models import Project, Member, Workflow, Release, Group
from dolphin.tests.helpers import LocalApplicationTestCase, \
    chat_mockup_server, chat_server_status


def callback(audit_logs):
    global logs
    logs = audit_logs
    auditor_callback(audit_logs)


class TestProject(LocalApplicationTestCase):
    __application__ = MiddleWare(Dolphin(), callback)

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )

        cls.workflow = Workflow(title='Default')

        cls.group = Group(title='Public', public=True)

        cls.release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-02-20T00:00:00',
            launch_date='2030-02-20T00:00:00',
            manager=cls.member,
            room_id=0,
            group=cls.group,
        )

        project1 = Project(
            workflow=cls.workflow,
            group=cls.group,
            release=cls.release1,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)
        session.commit()


    def test_create(self):
        self.login('member1@example.com')
        session = self.create_session()

        with chat_mockup_server(), self.given(
            'Createing a project',
            '/apiv1/projects',
            'CREATE',
            json=dict(
                workflowId=self.workflow.id,
                releaseId=1,
                title='My awesome project',
                description='A decription for my project',
                status='active',
                managerId=self.member.id,
                groupId=self.group.id,
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
            assert response.json['releaseCutoff'] == self.release1.cutoff

            created_project_id = response.json['id']
            created_project = session.query(Project).get(created_project_id)
            assert created_project.modified_by is None

            assert len(logs) == 2
            assert isinstance(logs[0], InstantiationLogEntry)
            assert isinstance(logs[1], RequestLogEntry)

            when(
                'Trying to create a project with secondary manager',
                json=Update(
                    title='project',
                    secondaryManagerId=self.member.id
                )
            )
            assert response.json['secondaryManagerId'] == self.member.id

            when(
                'Secondary manager is not found',
                json=Update(
                    title='New Project',
                    secondaryManagerId=0
                )
            )
            assert status == '650 Secondary Manager Not Found'

            when(
                'Manager id is null',
                json=Update(title='New Project', managerId=None)
            )
            assert status == '785 Manager Id Is Null'

            when(
                'Manager is not found',
                json=Update(title='New Project', managerId=0)
            )
            assert status == '608 Manager Not Found'

            when(
                'Maneger id is not in form',
                json=given - 'managerId' | dict(title='New Project')
            )
            assert status == '786 Manager Id Not In Form'

            when(
                'Workflow id is not in form',
                json=given - 'workflowId' | dict(title='New Project')
            )
            assert status == 200

            when(
                'Group id is not in form',
                json=given - 'groupId' | dict(title='New Project1')
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
            assert status == '616 Workflow Not Found'

            when(
                'Title format is wrong',
                json=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title is repetetive',
                json=given | dict(title='My first project')
            )
            assert status == '600 Repetitive Title'

            when(
                'Release ID type is wrong',
                json=given | dict(releaseId='Alphabetical', title='New title')
            )
            assert status == '750 Invalid Release Id Type'

            when(
                'Release not found with integer type',
                json=given | dict(releaseId=0, title='New title')
            )
            assert status == '607 Release Not Found'

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

