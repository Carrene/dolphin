from bddrest import status, response, when

from dolphin.models import Issue, Project, Member, Workflow, Phase, Tag, \
    Organization, DraftIssue
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        organization = Organization(
            title='First Organization'
        )

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
        )

        workflow = Workflow(title='default')

        phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow
        )
        session.add(phase1)

        phase2 = Phase(
            title='Triage',
            order=0,
            workflow=workflow
        )
        session.add(phase2)

        tag1 = Tag(title='tag1', organization=organization)
        tag2 = Tag(title='tag2', organization=organization)
        session.add(tag2)

        project = Project(
            workflow=workflow,
            member=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2,
            tags=[tag1]
        )
        session.add(issue1)

        cls.tag = tag1
        cls.project = project
        cls.draft_issue = DraftIssue()
        session.add(cls.draft_issue)
        session.commit()

    def test_patch(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Testing the patch method on issue',
            verb='PATCH',
            url='/apiv1/draftissues',
            json=[
              {
                'path': f'1/tags/{self.tag.id}',
                'op':'add',
                'value':{}
              },
              {
                'path': '1',
                'op':'finalize',
                'value': {
                    'title': 'Defined issue',
                    'status': 'in-progress',
                    'description': 'A description for defined issue',
                    'dueDate': '2200-2-20',
                    'kind': 'feature',
                    'days': 3,
                    'projectId': self.project.id,
                    'priority': 'high',
                }
              }
            ]
        ):
            assert status == 200
            assert len(response.json) == 2
            assert response.json[0]['id'] is not None
            assert response.json[1]['id'] is not None

            when(
                'One of requests response faces non 200 OK',
                json=[
                    dict(
                        op='ADD',
                        path='2/tags/100',
                        value={}
                    )
                ]
            )
            assert status == 404

