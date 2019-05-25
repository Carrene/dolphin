from os.path import join, dirname, abspath

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from sqlalchemy_media import StoreManager

from dolphin.models import Project, Member, Attachment, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')
maximum_image_path = join(this_dir, 'stuff', 'maximum-length.jpg')


class TestProject(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session(expire_on_commit=True)
        with StoreManager(session):
            attachment1 = Attachment(title='image', file=image_path)
            attachment2 = Attachment(title='image2', file=image_path)
            attachment3 = Attachment(title='image3', file=image_path)
            attachment4 = Attachment(title='image4', file=image_path)
            member1 = Member(
                title='First Member',
                email='member1@example.com',
                phone=123456789,
                password='123ABCabc',
                attachments=[
                    attachment1,
                    attachment2,
                    attachment3,
                    attachment4
                ]
            )

            workflow = Workflow(title='Default')
            group = Group(title='default')

            release = Release(
                title='My first release',
                description='A decription for my first release',
                cutoff='2030-2-20',
                launch_date='2030-2-20',
                manager=member1,
                room_id=0,
                group=group,
            )

            cls.project1 = Project(
                release=release,
                workflow=workflow,
                group=group,
                manager=member1,
                title='My first project',
                description='A decription for my project',
                room_id=1001,
                attachments=[attachment1, attachment2, attachment3]
            )
            cls.project2 = Project(
                release=release,
                workflow=workflow,
                group=group,
                manager=member1,
                title='My second project',
                description='A decription for my project',
                room_id=1002,
                attachments=[attachment4]
            )
            attachment3.soft_delete()
            session.add(cls.project1, cls.project2)
            session.commit()

    def test_delete_attachment(self):
        self.login('member1@example.com')

        with self.given(
            'List attachments of a project',
            f'/apiv1/projects/project_id:{self.project1.id}/files',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 2
            assert response.json[0]['id'] == 1

            when(
                'Try to sort the response in descending order',
                query=dict(sort='-id')
            )
            assert response.json[0]['id'] == 2

            when(
                'Try to filter the response using title',
                query=dict(id=2)
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == 2

            when(
                'Try to filter the response ignoring a title',
                query=dict(id='!2')
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] != 2

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['title'] == 'image2'

            when(
                'Test sorting before pagination',
                query=dict(sort='-id', take=1, skip=1)
            )
            assert response.json[0]['title'] == 'image'

