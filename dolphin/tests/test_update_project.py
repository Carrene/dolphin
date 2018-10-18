from bddrest import status, response, Update, when, given

from dolphin.models import Project, Member
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

        project1 = Project(
            member=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)

        project2 = Project(
            member=member1,
            title='My second project',
            description='A decription for my project',
            room_id=1002
        )
        session.add(project2)

        hidden_project = Project(
            member=member1,
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
                memberId=1,
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
                'Member not found with string type',
                form=given | dict(memberId='Alphabetical', title='New title')
            )
            assert status == 610
            assert status.text.startswith('Member not found')

            when(
                'Member is not found',
                form=Update(memberId=100)
            )
            assert status == 610
            assert status.text.startswith('Member not found')

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

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    form=given | dict(memberId=2)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    form=given | dict(memberId=2)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    form=given | dict(memberId=2)
                )
                assert status == '801 Chat Server Internal Error'

            with room_mockup_server():
                when(
                    'Room member is already added to room',
                    form=given | dict(memberId=2)
                )
                assert status == 200

            with self.given(
                'Updating project with empty form',
                '/apiv1/projects/id:2',
                'UPDATE',
                form=dict()
            ):
                assert status == '708 No Parameter Exists In The Form'

