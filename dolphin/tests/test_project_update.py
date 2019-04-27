from auditor import MiddleWare
from auditor.logentry import ChangeAttributeLogEntry
from auditor.context import Context as AuditLogContext
from auditor.logentry import RequestLogEntry, InstantiationLogEntry
from bddrest import status, response, when, given
from nanohttp.contexts import Context
from nanohttp import context

from dolphin import Dolphin
from dolphin.models import Project, Member, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server


def callback(audit_logs):
    global logs
    logs = audit_logs


class TestProject(LocalApplicationTestCase):
    __application__ = MiddleWare(Dolphin(), callback)

    @classmethod
    @AuditLogContext(dict())
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

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123457689,
            reference_id=2
        )
        session.add(cls.member2)

        cls.workflow1 = Workflow(title='Workflow1')
        cls.workflow2 = Workflow(title='Workflow2')
        session.add(cls.workflow2)

        cls.group1 = Group(title='Group1')
        cls.group2 = Group(title='Group2')
        session.add(cls.group2)

        cls.release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=cls.group1,
        )

        cls.release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=cls.group1,
        )

        cls.project1 = Project(
            release=cls.release1,
            workflow=cls.workflow1,
            group=cls.group1,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(cls.project1)

        project2 = Project(
            release=cls.release1,
            workflow=cls.workflow1,
            group=cls.group1,
            manager=cls.member1,
            title='My second project',
            description='A decription for my project',
            room_id=1002
        )
        session.add(project2)

        project3 = Project(
            release=cls.release2,
            workflow=cls.workflow1,
            group=cls.group1,
            manager=cls.member1,
            title='My third project',
            description='A decription for my project',
            room_id=1003
        )
        session.add(project2)

        project4 = Project(
            release=cls.release2,
            workflow=cls.workflow1,
            group=cls.group1,
            manager=cls.member1,
            title='My fourth project',
            description='A decription for my project',
            room_id=1004
        )
        session.add(project2)

        cls.hidden_project = Project(
            release=cls.release1,
            workflow=cls.workflow1,
            group=cls.group1,
            manager=cls.member1,
            title='My hidden project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(cls.hidden_project)
        session.commit()

    def test_update(self):
        self.login('member1@example.com')

        class Identity:
            def __init__(self, member):
                self.id = member.id
                self.reference_id = member.reference_id

        with Context({}):
            context.identity = Identity(self.member1)
            old_values = self.project1.to_dict()
            old_values['release'] = self.release1.title
            old_values['workflow'] = self.workflow1.title
            old_values['group'] = self.group1.title
            old_values['secondaryManager'] = None

        form = dict(
            title='My interesting project',
            description='A updated project description',
            status='active',
            releaseId=self.release2.id,
            workflowId=self.workflow2.id,
            groupId=self.group2.id,
            secondaryManagerId=self.member1.id,
        )

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Updating a project',
            f'/apiv1/projects/id:{self.project1.id}',
            'UPDATE',
            json=form
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting project'
            assert response.json['description'] == 'A updated project ' \
                'description'
            assert response.json['status'] == 'active'
            assert response.json['managerId'] == self.member1.id
            assert response.json['secondaryManagerId'] == self.member1.id

            session = self.create_session()
            member1 = session.query(Member).get(self.member1.id)
            assert len(logs) == 8
            form['release'] = self.release2.title
            form['workflow'] = self.workflow2.title
            form['group'] = self.group2.title
            form['secondaryManager'] = member1.title
            for log in logs:
                if isinstance(log, ChangeAttributeLogEntry):
                    assert log.old_value == old_values[log.attribute_key]
                    assert log.new_value == form[log.attribute_key]

            del form['release']
            del form['workflow']
            del form['group']
            del form['secondaryManager']

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title is repetetive',
                json=given - 'releaseId' | dict(title='My fourth project')
            )
            assert status == '600 Another project with title: "My fourth '\
                'project" is already exists.'

            when(
                'Title is repetetive in another release',
                json=given | dict(
                    title='My second project',
                    releaseId=self.release1.id
                )
            )
            assert status == '600 Another project with title: '\
                '"My second project" is already exists.'

            when(
                'Title format is wrong',
                json=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title length is more than limit',
                json=given | dict(title=((128 + 1) * 'a'))
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'Description length is more than limit',
                json=given | dict(
                    description=((8192 + 1) * 'a'),
                )
            )
            assert status == '703 At Most 8192 Characters Are Valid For ' \
                'Description'

            when(
                'Status value is invalid',
                json=given | dict(
                    status='progressing',
                )
            )
            assert status == '705 Invalid status value, only one of "active, '\
                'on-hold, queued, done" will be accepted'

            when(
                'Invalid parameter is in the form',
                json=given + \
                    dict(invalid_param='External parameter')
            )
            assert status == \
                '707 Invalid field, only following fields are accepted: ' \
                'title, description, status, releaseId, workflowId, groupId, ' \
                'managerId, secondaryManagerId'

            when(
                'Trying to update a project with secondary manager',
                json=given | dict(secondaryManagerId=self.member2.id)
            )
            assert response.json['secondaryManagerId'] == self.member2.id

            when(
                'Secondary manager is not found',
                json=given | dict(secondaryManagerId=0)
            )
            assert status == '650 Secondary Manager Not Found'

            when(
                'Trying to change the project manager',
                json=given | dict(managerId=self.member2.id)
            )
            assert response.json['managerId'] == self.member2.id

            when(
                'Manager id is null',
                json=given | dict(managerId=None)
            )
            assert status == '785 Manager Id Is Null'

            when(
                'Manager is not found',
                json=given | dict(managerId=0)
            )
            assert status == '608 Manager Not Found'

            when('Request is not authorized', authorization=None)
            assert status == 401

            when(
                'Update a hidden project',
                url_parameters=dict(id=self.hidden_project.id)
            )
            assert status == '746 Hidden Project Is Not Editable'

            with self.given(
                'Updating project with empty form',
                '/apiv1/projects/id:2',
                'UPDATE',
                json=dict()
            ):
                assert status == '708 No Parameter Exists In The Form'

