from auditor.context import Context as AuditLogContext
from bddrest import status, when, response

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Project, Member, Workflow, Group, Release


class TestProject(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member1)

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )

        cls.project1 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(cls.project1)

        cls.hidden_project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My hidden project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(cls.hidden_project)
        session.commit()

    def test_show(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Showing a hidden project',
            f'/apiv1/projects/id:{self.hidden_project.id}',
            'SHOW'
        ):
            assert status == 200
            assert response.json['removedAt'] == None

            when(
                'Showing a unhidden project',
                url_parameters=dict(id=self.project1.id)
            )
            assert status == '639 Project Already Shown'

            when(
                'Project not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'There is parameter is form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

