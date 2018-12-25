from bddrest import status, when, given, response

from dolphin.models import Release, Member, Project, Subscription, Workflow
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

        workflow = Workflow(title='default')
        session.add(workflow)
        session.flush()

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
        )
        session.add(release1)
        session.flush()

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
        )
        session.add(release2)

        project1 = Project(
            workflow_id=workflow.id,
            member=member,
            release=release1,
            title='My first project',
            description='A decription for my project',
            room_id=1000
        )
        session.add(project1)
        session.flush()

        project2 = Project(
            workflow_id=workflow.id,
            member=member,
            release=release2,
            title='My first project',
            description='A decription for my project',
            room_id=1000
        )
        session.add(project2)

        subscription1 = Subscription(
            subscribable=release1.id,
            member=member.id
        )
        session.add(subscription1)

        subscription2 = Subscription(
            subscribable=release2.id,
            member=member.id
        )
        session.add(subscription2)
        session.commit()

    def test_unsubscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Unsubscribe release',
            '/apiv1/releases/id:1',
            'UNSUBSCRIBE',
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
                'Release is not subscribed yet',
                url_parameters=dict(id=1),
            )
            assert status == '612 Not Subscribed Yet'

            when('Request is not authorized', authorization=None)
            assert status == 401

