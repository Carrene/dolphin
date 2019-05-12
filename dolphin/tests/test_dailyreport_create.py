from datetime import datetime

from bddrest import status, response, when, given
from auditor.context import Context as AuditLogContext

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
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        form = dict(
            note='Some summary',
            hours=2,
            itemId=self.item.id,
        )

        with oauth_mockup_server(), self.given(
            'Creating a dailyreport',
            '/apiv1/dailyreports',
            'CREATE',
            json=form
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['date'] == str(datetime.now().date())
            assert response.json['hours'] == form['hours']
            assert response.json['note'] == form['note']
            assert response.json['itemId'] == form['itemId']

            when(
                'Item id is null',
                json=given | dict(itemId=None)
            )
            assert status == '913 Item Id Is Null'

            when(
                'Item id is not in form',
                json=given - 'itemId'
            )
            assert status == '732 Item Id Not In Form'

            when(
                'Item is not found',
                json=given | dict(itemId=0)
            )
            assert status == '660 Item Not Found'

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Invalid parameter is in form',
                json=given | dict(parameter='invalid parameter')
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: hours, note and itemId'

            when(
                'Note length is less than limit',
                json=given | dict(note=(1024 + 1) * 'a'),
            )
            assert status == '902 At Most 1024 Characters Are Valid For Note'

            when(
                'Hours value type is wrong',
                json=given | dict(hours='a')
            )
            assert status == '900 Invalid Hours Type'

            when(
                'Hours value is less then 1',
                json=given | dict(hours=0)
            )
            assert status == '914 Hours Must Be Greater Than 0'

            when('Request is not authorized', authorization=None)
            assert status == 401

