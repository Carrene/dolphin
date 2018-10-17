from bddrest import status, response, when

from dolphin.models import Release, Member
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestRelease(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member)

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )
        session.add(release1)

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
        )
        session.add(release2)

        release3 = Release(
            title='My third release',
            description='A decription for my third release',
            cutoff='2030-2-20',
        )
        session.add(release3)
        session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List releases',
            '/apiv1/releases',
            'LIST'
        ):
            assert status == 200
            assert len(response.json) == 3

        with oauth_mockup_server(), self.given(
            'Sort releases by title',
            '/apiv1/releases',
            'LIST',
            query=dict(sort='title')
        ):
            assert response.json[0]['title'] == 'My first release'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'My third release'

        with oauth_mockup_server(), self.given(
            'Filter releases',
            '/apiv1/releases',
            'LIST',
            query=dict(sort='id', take=1, skip=2)
        ):
            assert response.json[0]['title'] == 'My third release'

            when(
                'List releases except one of them',
                query=dict(title='!My second release')
            )
            assert response.json[0]['title'] == 'My first release'

        with oauth_mockup_server(), self.given(
             'Issues pagination',
             '/apiv1/releases',
             'LIST',
             query=dict(sort='id', take=1, skip=2)
         ):
            assert response.json[0]['title'] == 'My third release'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'My first release'

            when('Request is not authorized', authorization=None)
            assert status == 401

