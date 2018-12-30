from bddrest import status, response, when

from dolphin.models import Issue, Project, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member)

        workflow = Workflow(title='default')

        project = Project(
            workflow=workflow,
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2016-2-20',
            kind='feature',
            days=2,
            room_id=3
        )
        session.add(issue2)

        issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of third issue',
            due_date='2020-2-20',
            kind='feature',
            days=3,
            room_id=4
        )
        session.add(issue3)
        session.commit()

    def test_list(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List issues',
            '/apiv1/issues',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

        with oauth_mockup_server(), self.given(
            'Sort issues by title',
            '/apiv1/issues',
            'LIST',
            query=dict(sort='title')
        ):
            assert response.json[0]['title'] == 'First issue'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'Third issue'

        with oauth_mockup_server(), self.given(
            'Filter issues',
            '/apiv1/issues',
            'LIST',
            query=dict(title='First issue')
        ):
            assert response.json[0]['title'] == 'First issue'

            when(
                'List issues except one of them',
                query=dict(title='!Second issue')
            )
            assert len(response.json) == 2

            when(
                'Filter based on a hybrid property',
                query=dict(boarding='delayed')
            )
            assert len(response.json) == 1

        with oauth_mockup_server(), self.given(
             'Issues pagination',
             '/apiv1/issues',
             'LIST',
             query=dict(take=1, skip=2)
         ):
            assert response.json[0]['title'] == 'Third issue'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'First issue'

            when('Request is not authorized', authorization=None)
            assert status == 401

