from bddrest import status, response, Update, when, Remove, given

from dolphin.models import Project, Member, Release
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

        project1 = Project(
            member=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(project1)

        hidden_project = Project(
            member=member1,
            title='My hidden project',
            description='A decription for my project',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(hidden_project)
        session.commit()

    def test_hide(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Hiding a project',
            '/apiv1/projects/id:1',
            'HIDE'
        ):
            session = self.create_session()
            project = session.query(Project) \
                .filter(Project.id == 1) \
                .one_or_none()
            assert status == 200
            project.assert_is_deleted()

            when(
                'Intended Project With String Type Not Found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when('Project not found', url_parameters=dict(id=100))
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

