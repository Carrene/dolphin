from os.path import join, dirname, abspath

from auditing.context import Context as AuditLogContext
from bddrest import status, response, when, Update
from sqlalchemy_media import StoreManager

from dolphin.models import Project, Member, Attachment, Workflow, Group, \
    Release, Issue
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')
maximum_image_path = join(this_dir, 'stuff', 'maximum-length.jpg')


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session(expire_on_commit=True)
        with StoreManager(session):
            cls.attachment1 = Attachment(title='image', file=image_path)
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
                    cls.attachment1,
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
            )

            project = Project(
                release=release,
                workflow=workflow,
                group=group,
                member=member1,
                title='My first project',
                description='A decription for my project',
                room_id=1001,
            )

            attachment3.soft_delete()

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                due_date='2020-2-20',
                kind='feature',
                days=1,
                room_id=2,
                attachments=[cls.attachment1, attachment2, attachment3]
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                due_date='2016-2-20',
                kind='feature',
                days=2,
                room_id=3,
                attachments=[attachment4]
            )
            session.add(cls.issue2)
            session.commit()

    def test_delete_issue_attachment(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Delete a project attachment',
            f'/apiv1/issues/issue_id:{self.issue1.id}/'
            f'files/id:{self.attachment1.id}',
            'DELETE',
        ):
            assert status == 200
            assert response.json['removedAt'] is not None
            assert response.json['file']['url'] is None

            when('Try to delete the same attachment')
            assert status == '629 Attachment Already Deleted'

            when('The attachment is not exist', url_parameters=Update(id=0))
            assert status == 404

            when(
                'The attachment id is invalid',
                url_parameters=Update(id='attachment')
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

