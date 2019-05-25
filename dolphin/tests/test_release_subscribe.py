from auditor.context import Context as AuditLogContext
from bddrest import status, when, given, response

from dolphin.models import Release, Member, Project, Workflow, Group
from dolphin.tests.helpers import LocalApplicationTestCase


class TestRelease(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(member)

        workflow = Workflow(title='Default')
        group = Group(title='default')

        cls.release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member,
            room_id=0,
            group=group,
        )
        session.add(cls.release1)

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member,
            room_id=0,
            group=group,
        )
        session.add(release2)
        session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with self.given(
            'Subscribe release',
            f'/apiv1/releases/id:{self.release1.id}',
            'SUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == self.release1.id
            assert response.json['isSubscribed'] == True

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

