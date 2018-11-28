from bddrest import status, response, when

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

        project1 = Project(
            member=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)
        session.commit()

    def test_get(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Getting a project',
            '/apiv1/projects/id:1',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == 1
            assert response.json['title'] == 'My first project'

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == 709

            when('Request is not authorized', authorization=None)
            assert status == 401

