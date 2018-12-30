from os.path import join, dirname, abspath

from bddrest import status, response, when
from sqlalchemy_media import StoreManager

from dolphin.models import Project, Member, Attachment, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')
maximum_image_path = join(this_dir, 'stuff', 'maximum-length.jpg')


class TestProject(LocalApplicationTestCase):

    @classmethod
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
                access_token='access token 1',
                phone=123456789,
                reference_id=2,
                attachments=[
                    attachment1,
                    attachment2,
                    attachment3,
                    attachment4
                ]
            )

            workflow = Workflow(title='default')
            session.add(workflow)
            session.flush()

            cls.project1 = Project(
                workflow_id=workflow.id,
                member=member1,
                title='My first project',
                description='A decription for my project',
                room_id=1001,
                attachments=[attachment1, attachment2, attachment3]
            )
            cls.project2 = Project(
                workflow_id=workflow.id,
                member=member1,
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

        with oauth_mockup_server(), self.given(
            'List attachments of a project',
            '/apiv1/projects/project_id:1/files',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 2
            assert response.json[0]['id'] == 2

            when(
                'Try to sort the response in descending order',
                query=dict(sort='-id')
            )
            assert response.json[0]['id'] == 3

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

