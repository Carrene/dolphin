from bddrest import status, response, when

from dolphin.models import Container, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestContainer(LocalApplicationTestCase):

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

        container1 = Container(
            member=member1,
            workflow=workflow1,
            title='My first container',
            description='A decription for my container',
            room_id=1001
        )
        session.add(container1)

        container2 = Container(
            member=member1,
            workflow=workflow1,
            title='My second container',
            description='A decription for my container',
            room_id=1002
        )
        session.add(container2)

        container3 = Container(
            member=member1,
            workflow=workflow1,
            title='My third container',
            description='A decription for my container',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(container3)
        session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List containers',
            '/apiv1/containers',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            with self.given(
                'Sort containers by phases title',
                '/apiv1/containers',
                'LIST',
                query=dict(sort='title')
            ):
                assert status == 200
                assert response.json[0]['title'] == 'My first container'

                when(
                    'Reverse sorting titles by alphabet',
                    query=dict(sort='-title')
                )
                assert response.json[0]['title'] == 'My third container'

            with self.given(
                'Filter containers',
                '/apiv1/containers',
                'LIST',
                query=dict(sort='id', title='My first container')
            ):
                assert response.json[0]['title'] == 'My first container'

                when(
                    'List containers except one of them',
                    query=dict(sort='id', title='!My awesome container')
                )
                assert response.json[0]['title'] == 'My first container'

            with self.given(
                'Container pagination',
                '/apiv1/containers',
                'LIST',
                query=dict(sort='id', take=1, skip=2)
            ):
                assert response.json[0]['title'] == 'My third container'

                when(
                    'Manipulate sorting and pagination',
                    query=dict(sort='-title', take=1, skip=2)
                )
                assert response.json[0]['title'] == 'My first container'

                when('Request is not authorized', authorization=None)
                assert status == 401

