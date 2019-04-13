from nanohttp import context
from nanohttp.contexts import Context
from auditor.context import Context as AuditLogContext
from bddrest import status, response, when

from dolphin.models import Issue, Project, Member, Workflow, Item, Phase, \
    Group, Release, Skill, Activity
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestActivity(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 1',
            phone=123456788,
            reference_id=2
        )
        session.add(cls.member2)

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = cls.member1

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                due_date='2020-2-20',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)
            session.flush()

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
            session.flush()

            cls.phase1 = Phase(
                workflow=workflow,
                title='phase 1',
                order=1,
                skill=skill,
            )
            session.add(cls.phase1)
            session.flush()

            item1 = Item(
                member_id=cls.member1.id,
                phase_id=cls.phase1.id,
                issue_id=cls.issue1.id,
            )
            session.add(item1)

            item2 = Item(
                member_id=cls.member1.id,
                phase_id=cls.phase1.id,
                issue_id=issue2.id,
            )
            session.add(item2)

            activity1 = Activity(
                item=item1
            )
            session.add(activity1)

            activity2 = Activity(
                item=item1
            )
            session.add(activity2)

            activity3 = Activity(
                item=item2
            )
            session.add(activity3)
            session.commit()

    def test_list(self):
        self.login(email=self.member1.email)

        with oauth_mockup_server(), self.given(
            f'List activities',
            f'/apiv1/issues/id:{self.issue1.id}/activities',
            f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] == 1
            assert response.json[1]['id'] == 2

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 2
            assert response.json[1]['id'] == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            self.logout()
            when('Request is not authorized', authorization=None)
            assert status == 401

            self.login(email=self.member2.email)
            when(
                'There is no time card for someone else',
                authorization=self._authentication_token
            )
            assert len(response.json) == 0
