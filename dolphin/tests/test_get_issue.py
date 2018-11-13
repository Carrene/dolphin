from bddrest import status, response, when

from dolphin.models import Issue, Member, Workflow, Container
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member)

        workflow1 = Workflow(title='First Workflow')

        container = Container(
            member=member,
            workflow=workflow1,
            title='My first container',
            description='A decription for my container',
            room_id=1
        )
        session.add(container)

        issue1 = Issue(
            container=container,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)
        session.commit()

    def test_get(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Getting a issue',
            '/apiv1/issues/id:2',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == 2
            assert response.json['title'] == 'First issue'

            when(
                'Intended container with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended container with string type not found',
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

