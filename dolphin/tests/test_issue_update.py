from auditor import MiddleWare
from auditor.context import Context as AuditLogContext
from auditor.logentry import ChangeAttributeLogEntry
from bddrest import status, when, given, response, Update
from nanohttp import context
from nanohttp.contexts import Context

from dolphin import Dolphin
from dolphin.middleware_callback import callback as auditor_callback
from dolphin.models import Issue, Project, Member, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server


def callback(audit_logs):
    global logs
    logs = audit_logs
    auditor_callback(audit_logs)


class TestIssue(LocalApplicationTestCase):
    __application__ = MiddleWare(Dolphin(), callback)

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member)

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member,
            room_id=0,
            group=group,
        )

        project1 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project1)

        issue1 = Issue(
            project=project1,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)

        cls.issue2 = Issue(
            project=project1,
            title='Second issue',
            description='This is description of second issue',
            kind='feature',
            days=2,
            room_id=3
        )
        session.add(cls.issue2)
        session.commit()

    def test_update(self):
        self.login(self.member.email)

        session = self.create_session()
        issue2 = session.query(Issue).get(self.issue2.id)

        class Identity:
            def __init__(self, member):
                self.id = member.id
                self.reference_id = member.reference_id

        with Context({}):
            context.identity = Identity(self.member)
            old_values = issue2.to_dict()

        form=dict(
            title='New issue',
            description='This is a description for new issue',
            kind='bug',
            days=4,
            priority='high',
        )
        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Update a issue',
            f'/apiv1/issues/id:{self.issue2.id}',
            'UPDATE',
            form=form,
        ):
            assert status == 200
            assert response.json['id'] == self.issue2.id
            assert response.json['priority'] == 'high'
            assert response.json['tags'] is not None
            assert response.json['modifiedAt'] is not None
            assert response.json['modifiedBy'] == self.member.reference_id

            assert len(logs) == 6
            for log in logs:
                if isinstance(log, ChangeAttributeLogEntry):
                    assert log.old_value == old_values[log.attribute_key]
                    assert log.new_value == form[log.attribute_key]

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
                'Title is the same of it already is',
                form=given | dict(title='Another issue')
            )
            assert status == 200

            when(
                'Title is repetitive',
                form=given | dict(title='First issue')
            )
            assert status == '600 Another issue with title: "First issue" '\
                'is already exists.'

            when(
                'Title format is wrong',
                form=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title length is more than limit',
                form=given | dict(title=((128 + 1) * 'a'))
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((8192 + 1) * 'a'),
                    title=('Another title')
                )
            )
            assert status == '703 At Most 8192 Characters Are Valid For '\
                'Description'

            when(
                'Invalid kind value is in form',
                form=given | dict(kind='enhancing', title='Another title')
            )
            assert status == '717 Invalid kind, only one of "feature, '\
                'bug" will be accepted'

            when(
                'Invalid stage value is in form',
                form=given + dict(stage='progressing') | \
                    dict(title='Another title')
            )
            assert status == '705 Invalid stage value, only one of "triage, ' \
                'backlog, working, on-hold" will be accepted'
            assert status.text.startswith('Invalid stage')

            when(
                'Invalid priority value is in form',
                form=Update(priority='no_priority')
            )
            assert status == '767 Invalid priority, only one of "low, '\
                'normal, high" will be accepted'

            when(
                'ProjectId in form',
                form=Update(projectId=self.issue2.project.id)
            )
            assert status == 200

            when(
                'Invalid parameter is in the form',
                form=given + dict(invalid_param='External parameter') | \
                    dict(title='Another title')
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: stage, isDone, description, phaseId, memberId, ' \
                'projectId, title, days, priority, kind'

            when('Request is not authorized', authorization=None)
            assert status == 401

            when('Updating project with empty form', form=dict())
            assert status == '708 No Parameter Exists In The Form'

