from auditor.context import Context as AuditLogContext
from bddrest import status, response, when
from nanohttp import context
from nanohttp.contexts import Context

from .helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server
from dolphin.models import Issue, Project, Member, Workflow, Phase, Tag, \
    Organization, Group, Release, Specialty, Skill


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        organization = Organization(
            title='First Organization'
        )

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
        )
        session.add(cls.member)
        session.commit()

        workflow = Workflow(title='default')
        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
        )

        group = Group(title='default')

        phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(phase1)

        phase2 = Phase(
            title='Triage',
            order=0,
            workflow=workflow,
            specialty=specialty,
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

        project = Project(
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

            cls.issue = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2,
                tags=[cls.tag1]
            )
            session.add(cls.issue)
            session.commit()

    def test_patch(self):
        self.login(self.member.email)

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Testing the patch method on issue',
            verb='PATCH',
            url='/apiv1/issues',
            json=[
                dict(
                    op='ADD',
                    path=f'{self.issue.id}/tags/{self.tag2.id}',
                    value={}
                ),
                dict(
                    op='REMOVE',
                    path=f'{self.issue.id}/tags/{self.tag1.id}',
                    value={}
                ),
                dict(
                    op='UPDATE',
                    path=f'{self.issue.id}',
                    value={
                        'title': 'sample title',
                        'priority': 'low',
                        'kind': 'bug',
                        'stage': 'on-hold',
                    }
                )
            ]
        ):
            assert status == 200
            assert len(response.json) == 3
            assert response.json[0]['id'] is not None
            assert response.json[1]['id'] is not None
            assert response.json[2]['id'] is not None

            when(
                'One of requests response faces non 200 OK',
                json=[
                    dict(
                        op='ADD',
                        path=f'{self.issue.id}/tags/0',
                        value={}
                    )
                ]
            )
            assert status == 404

            when(
                'JSONPatch subscribe',
                json=[
                    dict(path=f'{self.issue.id}', op='subscribe', value=None),
                    dict(path=f'{self.issue.id}', op='unsubscribe', value=None),
                ]
            )
            assert status == 200

            when(
                'JSONPatch subscribe with form',
                json=[
                    dict(
                        path=f'{self.issue.id}',
                        op='subscribe',
                        value=dict(form='Form'),
                    ),
                    dict(
                        path=f'{self.issue.id}',
                        op='unsubscribe',
                        value=dict(form='Form'),
                    ),
                ]
            )
            assert status == '709 Form Not Allowed'

