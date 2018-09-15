
from bddrest import status, response, Update, when, Remove

from dolphin.models import Item, Phase, Issue, Manager, Release, Project, \
    Resource, Team
from dolphin.tests.helpers import LocalApplicationTestCase


class TestItem(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        team = Team(
            title='Awesome team'
        )

        manager = Manager(
            title='First Manager',
            email='manager1@example.com',
            access_token='access token',
            phone=123456789
        )

        release = Release(
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        project = Project(
            manager=manager,
            releases=[release],
            title='My first project',
            description='A decription for my project',
            due_date='2020-2-20',
        )

        issue = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )

        resource = Resource(
            teams=[team],
            title='Developer',
            email='dev@example.com',
            access_token='access token',
            phone=987654321
        )

        phase = Phase(
            project=project,
            title='design',
            order=1,
        )

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

        with self.given(
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

