from bddrest import when, response, status

from ..models import Workflow, Phase, Resource
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestResource(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        workflow = Workflow(title='default')

        cls.phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow
        )

        cls.resource1 = Resource(
            title='First Resource',
            email='resource1@example.com',
            access_token='access token 1',
            phone=222222222,
            reference_id=2,
            phase=cls.phase1,
        )
        session.add(cls.resource1)

        resource2 = Resource(
            title='Second Resource',
            email='resource2@example.com',
            access_token='access token 2',
            phone=333333333,
            reference_id=3,
            phase=cls.phase1,
        )
        session.add(resource2)
        session.commit()

    def test_list(self):
        self.login(self.resource1.email)

        with oauth_mockup_server(), self.given(
           f'Getting list of resources',
           f'/apiv1/phases/id: {self.phase1.id}/resources',
           f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('Trying to pass with wrong id', url_parameters=dict(id=0))
            assert status == 404

            when('Type of id is invalid', url_parameters=dict(id='not-integer'))
            assert status == 404

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] == 1
            assert response.json[1]['id'] == 2

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 2
            assert response.json[1]['id'] == 1

            when('Trying pagination response', query=dict(take=1))
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            self.logout()
            when(
                'Trying with an unauthorized member',
                authorization=self._authentication_token
            )
            assert status == 401

