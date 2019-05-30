from datetime import datetime, timedelta

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, given

from dolphin.models import Member, Workflow, Skill, Group, Phase, Release, \
    Project, Issue, Item
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
            reference_id=1,
        )
        session.add(cls.member)

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase1)

        phase2 = Phase(
            title='backend',
            order=1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase2)

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

        cls.item1 = Item(
            issue_id=issue.id,
            phase_id=phase1.id,
            member_id=cls.member.id,
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
        )
        session.add(cls.item1)

        cls.item2 = Item(
            issue_id=issue.id,
            phase_id=phase2.id,
            member_id=cls.member.id,
            start_date=datetime.now().date() - timedelta(days=1),
            end_date=datetime.now().date() - timedelta(days=1),
        )
        session.add(cls.item2)
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        form = dict(
            hours=4.8,
            note='Some note',
        )

        with oauth_mockup_server(), self.given(
            f'Creating a dailyreport',
            f'/apiv1/items/item_id: {self.item1.id}/dailyreports',
            f'CREATE',
            json=form,
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['hours'] == form['hours']
            assert response.json['note'] == form['note']

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Intended timecard with string type not found',
                url_parameters=given | dict(item_id='Alphabetical')
            )
            assert status == 404

            when( 'Invalid parameter is in form',json=given | dict(a='a'))
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: hours, note'

            when('Note not in form', json=given - 'note')
            assert status == '930 Note Not In Form'

            when('Hours not in form', json=given - 'hours')
            assert status == '929 Hours Not In Form'

            when(
                'Note length is less than limit',
                json=given | dict(note=(1024 + 1) * 'a'),
            )
            assert status == '902 At Most 1024 Characters Are Valid For Note'

            when('Hours value type is wrong', json=given | dict(hours='a'))
            assert status == '915 Invalid Hours Type'

            when('Hours value is less then 1', json=given | dict(hours=0))
            assert status == '914 Hours Must Be Greater Than 0'

            when(
                'Trying to create a daily report out of period date',
                url_parameters=dict(item_id=self.item2.id),
            )
            assert status == '664 Invalid Date Period'

            when('Request is not authorized', authorization=None)
            assert status == 401

