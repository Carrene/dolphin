from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Issue, Project, Workflow, Phase, Tag, \
    Organization, DraftIssue, Group, Release, Specialty, Resource
from .helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        organization = Organization(
            title='First Organization'
        )

        specialty = Specialty(title='Project Manager')

        cls.member = Resource(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
            specialty=specialty,
        )
        session.add(cls.member)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
        group = Group(title='default')

        phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow,
            specialty=specialty
        )
        session.add(phase1)

        phase2 = Phase(
            title='Triage',
            order=0,
            workflow=workflow,
            specialty=specialty
        )
        session.add(phase2)

        cls.tag1 = Tag(title='tag1', organization=organization)
        session.add(cls.tag1)

        cls.tag2 = Tag(title='tag2', organization=organization)
        session.add(cls.tag2)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member,
            room_id=0,
            group=group,
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = cls.member

            issue1 = Issue(
                project=cls.project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2,
                tags=[cls.tag1]
            )
            session.add(issue1)

            cls.draft_issue = DraftIssue()
            session.add(cls.draft_issue)
            session.commit()

    def test_patch(self):
        self.login(self.member.email)

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Testing the patch method on issue',
            verb='PATCH',
            url='/apiv1/draftissues',
            json=[
              dict(
                path=f'{self.draft_issue.id}/tags/{self.tag1.id}',
                op='add',
                value={}
              ),
              dict(
                path=f'{self.draft_issue.id}',
                op='finalize',
                value={
                    'title': 'Defined issue',
                    'stage': 'on-hold',
                    'description': 'A description for defined issue',
                    'kind': 'feature',
                    'days': 3,
                    'projectId': self.project.id,
                    'priority': 'high',
               }
              )
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
                        path=f'{self.draft_issue.id}/tags/0',
                        value={}
                    )
                ]
            )
            assert status == 404

