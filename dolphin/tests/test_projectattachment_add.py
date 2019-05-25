import io
from os.path import join, dirname, abspath

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, Update, Remove

from dolphin.models import Project, Member, Workflow, Group, Release
from dolphin.tests.helpers import LocalApplicationTestCase


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')
maximum_image_path = join(this_dir, 'stuff', 'maximum-length.jpg')


class TestProject(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
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

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(cls.project)
        session.commit()

    def test_add_attachment(self):
        self.login('member1@example.com')

        with open(image_path, 'rb') as f, self.given(
            'add an attachment to a project',
            f'/apiv1/projects/id:{self.project.id}/files',
            'ATTACH',
            multipart=dict(
                title='example',
                attachment=io.BytesIO(f.read())
            )
        ):
            assert status == 200
            assert response.json['title'] == 'example'
            assert response.json['id'] is not None
            assert response.json['createdAt'] is not None
            assert 'isMine' in response.json

            with open(maximum_image_path, 'rb') as f:
                when(
                    'Image size is more than maximum length',
                    multipart=Update(
                        caption='This is caption',
                        attachment=io.BytesIO(f.read())
                    )
                )
                assert status == 413

            when(
                'Try to pass without sending the file',
                multipart=Remove('attachment')
            )
            assert status == '758 File Not In Form'

            when(
                'Title is more than 128 charecters',
                multipart=Update(title=(128 + 1) * 'a')
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'The project not exist with this id',
                url_parameters=dict(id=0)
            )
            assert status == 404

            with open(maximum_image_path, 'rb') as f:
                when(
                    'Image size is more than maximum length',
                    multipart=Update(
                        attachment=io.BytesIO(f.read())
                    )
                )
                assert status == 413

            when(
                'Try to pass without sending the file',
                multipart=Remove('attachment')
            )
            assert status == '758 File Not In Form'

            when(
                'Title is more than 128 charecters',
                multipart=Update(title=(128 + 1) * 'a')
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            with open(maximum_image_path, 'rb') as f:
                when(
                    'Image size is more than maximum length',
                    multipart=Update(
                        attachment=io.BytesIO(f.read())
                    )
                )
                assert status == 413

            when(
                'Try to pass without sending the file',
                multipart=Remove('attachment')
            )
            assert status == '758 File Not In Form'

            when(
                'Title is more than 128 charecters',
                multipart=Update(title=(128 + 1) * 'a')
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

