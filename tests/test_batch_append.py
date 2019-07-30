from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, given
from nanohttp.contexts import Context
from nanohttp import context

from dolphin.models import Workflow, Group, Release, Member, Issue, \
    Project, ReturnToTriageJob
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestBatch(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token',
            phone=123456789,
            reference_id=2,
        )

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=group,
        )

        cls.project1 = Project(
            release=release1,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001,
        )
        session.add(cls.project1)
        session.commit()

        with Context(dict()):
            context.identity = cls.member1

            cls.issue1 = Issue(
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2,
            )
            cls.issue2 = Issue(
                title='second issue',
                description='This is description of second issue',
                kind='feature',
                days=1,
                room_id=2,
            )
            cls.issue3 = Issue(
                title='third issue',
                description='This is description of third issue',
                kind='feature',
                days=1,
                room_id=2,
                stage='backlog',
                batch=1,
            )

            cls.project1.issues.append(cls.issue1)
            cls.project1.issues.append(cls.issue2)
            cls.project1.issues.append(cls.issue3)
            cls.returntotriage = ReturnToTriageJob(
                at=datetime.now(),
                issue=cls.issue3,
            )
            session.commit()

    def test_append(self):
        session = self.create_session()
        self.login('member1@example.com')
        batch_id = 1

        with oauth_mockup_server(), self.given(
            'Appending a batch that have before',
            f'/apiv1/projects/project_id: {self.project1.id}' \
            f'/batches/batch_id: {batch_id}',
            'APPEND',
            json=dict(
                issueIds=self.issue1.id
            )
        ):
            assert status == 200
            assert response.json['id'] == batch_id
            assert response.json['projectId'] == self.project1.id
            assert len(response.json['issueIds']) == 2

            when(
                'Appending a batch without have before',
                url_parameters=dict(project_id=self.project1.id, batch_id=2),
                json=dict(issueIds=self.issue2.id),
            )
            assert status == 200
            assert response.json['id'] == 2
            assert response.json['projectId'] == self.project1.id
            assert len(response.json['issueIds']) == 1

            when(
                'Trying to pass without issue id',
                json=given - 'issueIds'
            )
            assert status == '723 Issue Id Not In Form'

            when(
                'Trying to pass with invalid issue id type',
                json=given | dict(issueIds='a')
            )
            assert status == '722 Invalid Issue Id Type'

            when(
                'Trying to pass with none issue id',
                json=given | dict(issueIds=None)
            )
            assert status == '775 Issue Id Is Null'

            when(
                'Issue is not found',
                json=given | dict(issueIds=0)
            )
            assert status == '605 Issue Not Found: 0'

            when(
                'Inended batch with string type not found',
                url_parameters=dict(
                    project_id=self.project1.id,
                    batch_id='Alaphabet'
                ),
            )
            assert status == 404

            when(
                'Inended batch with string type not found',
                url_parameters=dict(project_id=0, batch_id=2),
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

