from bddrest import status, response, when

from dolphin.models import Batch, Issue, Project
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestBatch(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member@example.com',
            access_token='access token',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member)

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(cls.project)

        cls.issue1 = Issue(
            project=cls.project,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)

        cls.issue2 = Issue(
            project=cls.peoject,
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

        with oauth_mockup_server(), self.given(
            'Appending a batch',
            f'/apiv1/batches/batch_id: {self.batch.id}',
            'APPEND',
            form=dict(
                issueId=[1, 2],
            )
        ):
            assert status == 200
            assert response.json['id'] is not None,
            assert response.json['title'] == self.batch.title
            assert response.json['projectId'] == self.project.id

            issues = response.json['issues']
            assert [x for x in issues['id'] if x == self.issue1.id]
            assert [x for x in issues['id'] if x == self.issue2.id]

            when('Request is not authorized', authorization=None)
            assert status == 401

