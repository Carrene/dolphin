from auditor.context import Context as AuditLogContext
from bddrest import status, when, response

from dolphin.models import Release, Member, Group
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

    def test_abort(self):
        self.login('member1@example.com')

        with self.given(
            'Aborting a release',
            f'/apiv1/releases/id:{self.release.id}',
            'ABORT'
        ):
            assert status == 200
            assert response.json['id'] == self.release.id

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
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            session = self.create_session()
            release = session.query(Release) \
                .filter(Release.id == 1) \
                .one_or_none()
            assert release is None

            when('Request is not authorized', authorization=None)
            assert status == 401

