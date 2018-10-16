from bddrest import status, response, when, Remove, given

from dolphin.models import Project, Member, Release
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status, \
    room_mockup_server


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

        project1 = Project(
            member=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)

        project2 = Project(
            member=member1,
            title='My second project',
            description='A decription for my project',
            room_id=1002
        )
        session.add(project2)

        project3 = Project(
            member=member1,
            title='My third project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(project3)
        session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List projects',
            '/apiv1/projects',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            with self.given(
                'Sort projects by phases title',
                '/apiv1/projects',
                'LIST',
                query=dict(sort='title')
            ):
                assert status == 200
                assert response.json[0]['title'] == 'My first project'

                when(
                    'Reverse sorting titles by alphabet',
                    query=dict(sort='-title')
                )
                assert response.json[0]['title'] == 'My third project'

            with self.given(
                'Filter projects',
                '/apiv1/projects',
                'LIST',
                query=dict(sort='id', title='My first project')
            ):
                assert response.json[0]['title'] == 'My first project'

                when(
                    'List projects except one of them',
                    query=dict(sort='id', title='!My awesome project')
                )
                assert response.json[0]['title'] == 'My first project'

            with self.given(
                'Project pagination',
                '/apiv1/projects',
                'LIST',
                query=dict(sort='id', take=1, skip=2)
            ):
                assert response.json[0]['title'] == 'My third project'

                when(
                    'Manipulate sorting and pagination',
                    query=dict(sort='-title', take=1, skip=2)
                )
                assert response.json[0]['title'] == 'My first project'

                when('Request is not authorized', authorization=None)
                assert status == 401

