from bddrest import status, response, Update, when, given

from dolphin.models import Project, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status, \
    room_mockup_server


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
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123457689,
            reference_id=3
        )
        session.add(member2)

        workflow1 = Workflow(title='First Workflow')

        project1 = Project(
            member=member1,
            workflow=workflow1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)

        project2 = Project(
            member=member1,
            workflow=workflow1,
            title='My second project',
            description='A decription for my project',
            room_id=1002
        )
        session.add(project2)

        hidden_project = Project(
            member=member1,
            workflow=workflow1,
            title='My hidden project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(hidden_project)
        session.commit()

    def test_update(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Updating a project',
            '/apiv1/projects/id:1',
            'UPDATE',
            form=dict(
                title='My interesting project',
                description='A updated project description',
                status='active',
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting project'
            assert response.json['description'] == 'A updated project ' \
                'description'
            assert response.json['status'] == 'active'

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended project with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title is repetetive',
                form=Update(title='My second project')
            )
            assert status == 600
            assert status.text.startswith('Another project with title')

            when(
                'Title format is wrong',
                form=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title length is more than limit',
                form=Update(
                    title=((50 + 1) * 'a')
                )
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is more than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when(
                'Status value is invalid',
                form=given | dict(
                    status='progressing',
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when(
                'Invalid parameter is in the form',
                form=given + \
                    dict(invalid_param='External parameter')
            )
            assert status == 707
            assert status.text.startswith('Invalid field')

            when('Request is not authorized', authorization=None)
            assert status == 401

            when(
                'Update a hidden project',
                url_parameters=dict(id=3)
            )
            assert status == '746 Hidden Project Is Not Editable'

            with self.given(
                'Updating project with empty form',
                '/apiv1/projects/id:2',
                'UPDATE',
                form=dict()
            ):
                assert status == '708 No Parameter Exists In The Form'

