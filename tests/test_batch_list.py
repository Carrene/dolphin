from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from nanohttp import context
from nanohttp.contexts import Context

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Project, Member, Workflow, Issue, Group, Release, \
    Specialty


class TestBatch(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=222222222,
            reference_id=3,
        )
        session.add(member2)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
        group = Group(title='default')

        cls.release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )

        cls.project1 = Project(
            release=cls.release1,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            status='active',
            room_id=1001,
        )
        session.add(cls.project1)
        session.flush()

        cls.project2 = Project(
            release=cls.release1,
            workflow=workflow,
            group=group,
            manager=member2,
            title='My second project',
            description='A decription for my project',
            status='active',
            room_id=1002,
        )
        session.add(cls.project2)

        with Context(dict()):
            context.identity = member1

            cls.issue1 = Issue(
                project=cls.project1,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2,
                batch=1,
            )
            session.add(cls.issue1)

            issue2 = Issue(
                project=cls.project1,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=2,
                room_id=3,
                batch=1,
            )
            session.add(issue2)

            issue3 = Issue(
                project=cls.project1,
                title='Third issue',
                description='This is description of third issue',
                kind='feature',
                days=1,
                room_id=2,
                batch=2,
            )
            session.add(issue3)
            session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List batches',
            f'/apiv1/projects/project_id: {self.project1.id}/batches',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2
            assert response.json[0]['stage'] == 'triage'
            assert response.json[1]['stage'] == 'triage'

            when(
                'Inended batch with string type not found',
                url_parameters=dict(project_id=0),
            )
            assert status == 404

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

