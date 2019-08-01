from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, given
from nanohttp import context
from nanohttp.contexts import Context

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Workflow, Group, Release, Member, Issue, \
    Project


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
                batch=1,
                stage='triage',
                is_batch_leader=True,
                project=cls.project1,
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=1,
                room_id=3,
                batch=1,
                stage='triage',
                project=cls.project1,
            )
            session.add(cls.issue1)
            session.commit()

    def test_remove(self):
        session = self.create_session()
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'Removing a batch',
            f'/apiv1/projects/project_id: {self.project1.id}/batches',
            'REMOVE',
            json=dict(
                issueId=self.issue1.id
            )
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['stage'] == self.issue1.stage
            assert response.json['projectId'] == self.project1.id
            assert self.issue1.id not in response.json['issueIds']
            assert not session.query(Issue).get(self.issue1.id).batch
            assert session.query(Issue) \
                .filter(Issue.id == self.issue1.id) \
                .filter(Issue.is_batch_leader == None) \
                .one()
            assert session.query(Issue) \
                .filter(Issue.id != self.issue1.id) \
                .filter(Issue.is_batch_leader == True) \
                .one()

            when(
                'Trying to pass without issue id',
                json=given - 'issueId',
            )
            assert status == '723 Issue Id Not In Form'

            when(
                'Trying to pass with invalid issue id type',
                json=given | dict(issueId='a'),
            )
            assert status == '722 Invalid Issue Id Type'

            when(
                'Trying to pass with none issue id',
                json=given | dict(issueId=None),
            )
            assert status == '775 Issue Id Is Null'

            when(
                'Intended issue not found',
                json=given | dict(issueId=0),
            )
            assert status == '605 Issue Not Found'

            when(
                'Intended project not found',
                url_parameters=dict(project_id=0),
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

