from bddrest import status, response, when

from dolphin.models import Release, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestProject(LocalApplicationTestCase):

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

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )
        session.add(release)
        session.commit()

    def test_get(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Getting a release',
            '/apiv1/releases/id:1',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == 1
            assert response.json['title'] == 'My first release'

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

