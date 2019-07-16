from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, given
from nanohttp.contexts import Context
from nanohttp import context

from dolphin.models import Workflow, Group, Release, Member, Batch, Issue, \
    Project
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

        cls.batch1 = Batch(title='02')
        cls.batch2 = Batch(title='03')
        cls.project1.batches.append(cls.batch1)
        cls.project1.batches.append(cls.batch2)

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

            cls.project1.issues.append(cls.issue1)
            cls.project1.issues.append(cls.issue2)
            session.commit()

    def test_append(self):
        session = self.create_session()
        self.login('member1@example.com')
        title = '10'

        with oauth_mockup_server(), self.given(
            'Appending a batch',
            f'/apiv1/batches/id: {title}',
            'APPEND',
            json=dict(
                issueIds=self.issue1.id
            )
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == title
            assert response.json['projectId'] == self.project1.id
            assert self.issue1.id in response.json['issueIds']
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
                'Inended batch with integer type not found',
                url_parameters=dict(id=101)
            )
            assert status == '936 Invalid Batch More Than 100'

            when(
                'Inended batch with string type not found',
                url_parameters=dict(id='Alaphabet')
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

            session = self.create_session()
            assert session.query(Batch) \
                .filter(Batch.project_id == self.project1.id) \
                .order_by(Batch.id.desc()) \
                .first() != self.batch2

            when(
                'Appending a batch',
                url_parameters=dict(id=self.batch1.title),
                json=dict(issueIds=self.issue2.id)

            )
            assert response.json['id'] is not None
            assert response.json['title'] == self.batch1.title
            assert response.json['projectId'] == self.project1.id
            assert self.issue2.id in response.json['issueIds']
            assert len(response.json['issueIds']) == 1

