from auditor.context import Context as AuditLogContext
from bddrest import status, response, when

from dolphin.models import Release, Member, Workflow, Group
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

        group = Group(title='default')

        cls.release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member,
            room_id=0,
            group=group,
        )
        session.add(cls.release)
        session.commit()

    def test_get(self):
        self.login('member1@example.com')

        with self.given(
            'Getting a release',
            f'/apiv1/releases/id:{self.release.id}',
            'GET'
        ):
            assert status == 200
            assert response.json['id'] == self.release.id
            assert response.json['title'] == 'My first release'

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

