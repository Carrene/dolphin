from datetime import datetime

from bddrest import when, response, status
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Dailyreport, Workflow, Skill, Group, Phase, \
    Release, Project, Issue, Item
from dolphin.tests.helpers import LocalApplicationTestCase


class TestDailyreport(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)

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

        issue = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue)
        session.flush()

        cls.item = Item(
            issue_id=issue.id,
            phase_id=phase.id,
            member_id=cls.member.id,
        )
        session.add(cls.item)

        dailyreport1 = Dailyreport(
            date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
            hours=1,
            note='note for dailyreport1',
            item=cls.item,
        )
        session.add(dailyreport1)

        dailyreport2 = Dailyreport(
            date=datetime.strptime('2019-1-3', '%Y-%m-%d').date(),
            hours=2,
            note='note for dailyreport2',
            item=cls.item,
        )
        session.add(dailyreport2)

        dailyreport3 = Dailyreport(
            date=datetime.strptime('2019-1-4', '%Y-%m-%d').date(),
            hours=3,
            note='note for dailyreport3',
            item=cls.item,
        )
        session.add(dailyreport3)
        session.commit()

    def test_list(self):
        self.login(self.member.email, self.member.password)
        session = self.create_session()

        with self.given(
            'List of dailyreports',
            f'/apiv1/items/item_id: {self.item.id}/dailyreports',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 4
            assert session.query(Dailyreport) \
                .filter(Dailyreport.date == datetime.now().date()) \
                .one()

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

