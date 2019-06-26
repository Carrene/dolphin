from datetime import datetime, timedelta

from bddrest import when, response, status
from auditor.context import Context as AuditLogContext
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Member, Dailyreport, Workflow, Skill, Group, Phase, \
    Release, Project, Issue, Item, IssuePhase
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestDailyreport(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(cls.member)
        session.commit()

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

        phase = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase)

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

            issue = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(issue)

            issue_phase1 = IssuePhase(
                issue=issue,
                phase=phase,
            )
            session.add(issue_phase1)

            one_day = timedelta(days=1)
            cls.item = Item(
                issue_phase=issue_phase1,
                member=cls.member,
                start_date=datetime.now().date() - 4 * timedelta(days=1),
                end_date=datetime.now().date(),
            )
            session.add(cls.item)

            dailyreport1 = Dailyreport(
                date=datetime.now().date() - 4 * timedelta(days=1),
                hours=1,
                note='note for dailyreport1',
                item=cls.item,
            )
            session.add(dailyreport1)

            dailyreport2 = Dailyreport(
                date=datetime.now().date() - 3 * timedelta(days=1),
                hours=2,
                note='note for dailyreport2',
                item=cls.item,
            )
            session.add(dailyreport2)

            dailyreport3 = Dailyreport(
                date=datetime.now().date() - 2 * timedelta(days=1),
                hours=3,
                note='note for dailyreport3',
                item=cls.item,
            )
            session.add(dailyreport3)
            session.commit()

    def test_list(self):
        self.login(self.member.email)
        session = self.create_session()

        with oauth_mockup_server(), self.given(
            'List of dailyreports',
            f'/apiv1/items/item_id: {self.item.id}/dailyreports',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] < response.json[1]['id']

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] > response.json[1]['id']

            when('Trying pagination response', query=dict(take=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert response.json[0]['id'] == 2
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Request is not authorized', authorization=None)
            assert status == 401

