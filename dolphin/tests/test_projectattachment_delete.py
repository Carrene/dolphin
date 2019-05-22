from os.path import join, dirname, abspath

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, Update
from sqlalchemy_media import StoreManager

from dolphin.models import Project, Member, Attachment, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')
maximum_image_path = join(this_dir, 'stuff', 'maximum-length.jpg')


class TestProject(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        cls.session = cls.create_session(expire_on_commit=True)
        with StoreManager(cls.session):
            cls.attachment = Attachment(title='image', file=image_path)
            member1 = Member(
                title='First Member',
                email='member1@example.com',
                phone=123456789,
                attachments=[cls.attachment]
            )

            workflow = Workflow(title='default')
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
                attachments=[cls.attachment]
            )
            cls.session.add(cls.project1)
            cls.session.commit()

    def test_delete_attachment(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Delete a project attachment',
            f'/apiv1/projects/project_id:{self.project1.id}/files/id:1',
            'DELETE',
        ):
            assert status == 200
            assert response.json['removedAt'] is not None
            assert response.json['file']['url'] is None

            when('Try to delete the same attachment')
            assert status == '629 Attachment Already Deleted'

            when('The attachment is not exist', url_parameters=Update(id=2))
            assert status == 404

            when(
                'The attachment id is invalid',
                url_parameters=Update(id='attachment')
            )
            assert status == 404

