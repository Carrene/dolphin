from bddrest import status, when, given, response

from dolphin.models import Issue, Project, Member
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

        project = Project(
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
            days=1
        )
        session.add(issue1)

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2
        )
        session.add(issue2)
        session.commit()

    def test_update(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Update a issue',
            '/apiv1/issues/id:2',
            'UPDATE',
            form=dict(
                title='New issue',
                description='This is a description for new issue',
                dueDate='2200-12-12',
                kind='feature',
                days=4,
            )
        ):
            assert status == 200
            assert response.json['id'] == 2

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
                form=given | dict(title='Another issue')
            )
            assert status == 404

            when(
                'Title is repetitive',
                form=given | dict(title='Second issue')
            )
            assert status == 600
            assert status.text.startswith('Another issue with title')

            when(
                'Title format is wrong',
                form=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                    title=('Another title')
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For '\
                'Description'

            when(
                'Due date format is wrong',
                form=given | dict(
                    dueDate='20-20-20',
                    title='Another title'
                )
            )
            assert status == '701 Invalid Due Date Format'

            when(
                'Invalid kind value is in form',
                form=given | dict(kind='enhancing', title='Another title')
            )
            assert status == 717
            assert status.text.startswith('Invalid kind')

            when(
                'Invalid status value is in form',
                form=given + dict(status='progressing') | \
                    dict(title='Another title')
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when(
                'Invalid parameter is in the form',
                form=given + dict(invalid_param='External parameter') | \
                    dict(title='Another title')
            )
            assert status == 707
            assert status.text.startswith('Invalid field')

            when('Request is not authorized', authorization=None)
            assert status == 401

        with oauth_mockup_server(), self.given(
            'Updating project with empty form',
            '/apiv1/issues/id:2',
            'UPDATE',
            form=dict()
        ):
            assert status == '708 No Parameter Exists In The Form'

