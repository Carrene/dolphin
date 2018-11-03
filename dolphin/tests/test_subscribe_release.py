from bddrest import status, when, given, response

from dolphin.models import Release, Member, Project, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server


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

        workflow1 = Workflow(title='First Workflow')

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

        project1 = Project(
            member=member,
            workflow=workflow1,
            release=release1,
            title='My first project',
            description='A decription for my project',
            room_id=1000
        )
        session.add(project1)

        project2 = Project(
            member=member,
            workflow=workflow1,
            release=release2,
            title='My first project',
            description='A decription for my project',
            room_id=1000
        )
        session.add(project2)
        session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Subscribe release',
            '/apiv1/releases/id:1',
            'SUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == 1

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(parameter='Any parameter')
            )
            assert status == '709 Form Not Allowed'

            when(
                'Release is already subscribed',
                url_parameters=dict(id=1),
            )
            assert status == '611 Already Subscribed'

            when('Request is not authorized', authorization=None)
            assert status == 401

