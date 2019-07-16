from bddrest import status, response, when

from dolphin.models import Member, Workflow
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestWorkflow(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member)

        cls.workflow = Workflow(
            title='My first workflow',
            description='A decription for my first workflow',
        )
        session.add(cls.workflow)
        session.commit()

    def test_get(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'Getting a workflow',
            f'/apiv1/workflows/id:{self.workflow.id}',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == self.workflow.id
            assert response.json['title'] == self.workflow.title
            assert response.json['description'] == self.workflow.description

            when(
                'Intended workflow with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended workflow with string type not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

