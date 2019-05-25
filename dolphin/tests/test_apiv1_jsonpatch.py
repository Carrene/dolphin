from auditor.context import Context as AuditLogContext
from bddrest import status, response, when

from dolphin.models import Project, Member, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase


class TestProject(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=group,
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(cls.project)
        session.commit()

    def test_get(self):
        self.login(self.member1.email, self.member1.password)

        with self.given(
            'Testing the patch method on APIv1',
            verb='PATCH',
            url='/apiv1',
            json=[
                dict(
                    op='GET',
                    path='releases/1'
                ),
                dict(
                    op='GET',
                    path='projects/2'
                ),
            ]
        ):
            assert status == 200
            assert len(response.json) == 2

            when(
                'One of requests response faces non 200 OK',
                json=[
                    dict(
                        op='GET',
                        path='projects/0'
                    )
                ]
            )
            assert status == 404

