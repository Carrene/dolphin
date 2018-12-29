import io
from os.path import join, dirname, abspath

from bddrest import status, response, when, Update, Remove

from dolphin.models import Project, Member
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')
maximum_image_path = join(this_dir, 'stuff', 'maximum-length.jpg')


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

        project1 = Project(
            member=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)
        session.commit()

    def test_add_attachment(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), open(image_path, 'rb') as f, self.given(
            'add an attachment to a project',
            '/apiv1/projects/id:1/files',
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
                'Title is more than 50 charecters',
                multipart=Update(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'


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
                'Title is more than 50 charecters',
                multipart=Update(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

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
                'Title is more than 50 charecters',
                multipart=Update(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

