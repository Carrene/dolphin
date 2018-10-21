from bddrest import status, when, response

from dolphin.models import Project, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestProject(LocalApplicationTestCase):

    @classmethod
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

        workflow1 = Workflow(title='First Workflow')

        project1 = Project(
            member=member1,
            workflow=workflow1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)

        hidden_project = Project(
            member=member1,
            workflow=workflow1,
            title='My hidden project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(hidden_project)
        session.commit()

    def test_show(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Showing a unhidden project',
            '/apiv1/projects/id:2',
            'SHOW'
        ):
            assert status == 200
            assert response.json['removedAt'] == None

            when(
                'Project not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'There is parameter is form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

