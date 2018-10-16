from bddrest import status, when, given

from dolphin.models import Release, Member, Project, Subscription
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


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
        session.flush()

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
        )
        session.add(release2)

        project1 = Project(
            member=member,
            release=release1,
            title='My first project',
            description='A decription for my project',
            room_id=1000
        )
        session.add(project1)
        session.flush()

        project2 = Project(
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

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Unsubscribe release',
            '/apiv1/releases/id:1',
            'UNSUBSCRIBE',
            form=dict(memberId=1)
        ):
            assert status == 200

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
                'Member id not in form',
                form=given - 'memberId'
            )
            assert status == '735 Member Id Not In Form'

            when(
                'Member not found',
                form=given | dict(memberId=100)
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member id type is invalid',
                form=given | dict(memberId='Alphabetical')
            )
            assert status == '736 Invalid Member Id Type'

            when(
                'Issue is not subscribed yet',
                url_parameters=dict(id=1),
                form=given | dict(memberId=1)
            )
            assert status == '612 Not Subscribed Yet'

            when('Request is not authorized', authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    url_parameters=dict(id=2)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=2)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=2)
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('611 Member Not Found'):
                when(
                    'Room member is not found',
                    url_parameters=dict(id=2)
                )
                assert status == 200

