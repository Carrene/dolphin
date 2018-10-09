
from bddrest import status, response, Update, when, Remove

from dolphin.models import Item, Phase, Issue, Manager, Release, Project, \
    Resource, Team
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestItem(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        team = Team(
            title='Awesome team'
        )
        session.add(team)

        manager = Manager(
            title='First Manager',
            email='manager1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(manager)

        release = Release(
            title='My first release',
            description='A decription for my release',
            cutoff='2030-2-20',
        )
        session.add(release)

        project = Project(
            manager=manager,
            release=release,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

        issue = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )
        session.add(issue)

        resource = Resource(
            teams=[team],
            title='Developer',
            email='dev@example.com',
            access_token='access token',
            phone=987654321,
            reference_id=2
        )
        session.add(resource)

        phase = Phase(
            project=project,
            title='design',
            order=1,
        )
        session.add(phase)

        item = Item(
            resource=resource,
            phase=phase,
            issue=issue,
            status='in-progress',
            end='2020-2-2'
        )
        session.add(item)
        session.commit()

    def test_update(self):
        self.login('manager1@example.com')

        with oauth_mockup_server(), self.given(
            'Update status of an item',
            '/apiv1/items/id:1',
            'UPDATE',
            form=dict(
                status='complete'
            )
        ):
            assert status == 200
            assert response.json['status' ] == 'complete'

            when(
                'Status is not in form',
                form=Remove('status')
            )
            assert status == '719 Status Not In Form'

            when(
                'Invalid status value is in the form',
                form=Update(status='completing')
            )
            assert status == 705
            assert status.text.startswith('Invalid status value')

            when('Request is not authorized', authorization=None)
            assert status == 401

