from bddrest import status, response, when

from dolphin.models import Workflow, Group, Release, Member, Batch, Issue, \
    Project
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestBatch(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member@example.com',
            access_token='access token',
            phone=123456789,
            reference_id=2
        )

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )

        project1 = Project(
            release=release1,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)

        cls.issue1 = Issue(
            project=project1,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)

        cls.issue2 = Issue(
            project=project1,
            title='second issue',
            description='This is descripthion of second issue',
            kind='feature',
            days=1,
            room_id=2,
        )
        session.add(cls.issue2)

        cls.batch = Batch(
            title='01',
        )
        session.add(cls.batch)
        session.commit()

    def test_append(self):
        self.login(self.member.email)
        issues = [self.issue1.id, self.issue2.id]

        with oauth_mockup_server(), self.given(
            'Appending a batch',
            f'/apiv1/batches/batch_id: {self.batch.id}',
            'APPEND',
            form=dict(
                issueId=issues,
            )
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == self.batch.title
            assert response.json['projectId'] == self.project.id

            issues = response.json['issues']
            assert [x for x in issues['id'] if x == self.issue1.id]
            assert [x for x in issues['id'] if x == self.issue2.id]

            when(
                'Trying to pass without issue id',
                form=given - 'issueId'
            )
            assert status == '723 Issue ID Not In Form'

            when(
                'Trying to pass with null issue id',
                form=dict(issueId=None)
            )
            assert status == '775 Issue Id Is None'

            when(
                'Trying to pass with wrong type',
                form=dict(issueId='issue1')
            )
            assert status == '722 Inavlid Issue Id Type'

            when(
                'Intended batch with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Intended batch with integer type not found',
                url_parameters=dict(id=0),
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

