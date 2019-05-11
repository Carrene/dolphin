import datetime

from bddrest import status, response, when, given
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Workflow, Skill, Group, Phase, Release, \
    Project, Issue, Item
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestTimecard(LocalApplicationTestCase):

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
            startDate=datetime.datetime.now().isoformat(),
            endDate=datetime.datetime.now().isoformat(),
            summary='Some summary',
            estimatedTime=2,
            itemId=self.item.id,
        )

        with oauth_mockup_server(), self.given(
            'Creating a timecard',
            '/apiv1/timecards',
            'CREATE',
            json=form
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['startDate'] == form['startDate']
            assert response.json['endDate'] == form['endDate']
            assert response.json['estimatedTime'] == form['estimatedTime']
            assert response.json['summary'] == form['summary']
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
                'Summary length is less than limit',
                json=given | dict(summary=(1024 + 1) * 'a'),
            )
            assert status == '902 At Most 1024 Characters Are Valid For ' \
                'Summary'

            when(
                'Trying to pass without start date',
                json=given - 'startDate',
            )
            assert status == '792 Start Date Not In Form'

            when(
                'Trying to pass without end date',
                json=given - 'endDate',
            )
            assert status == '793 End Date Not In Form'

            when(
                'Trying to pass without summary',
                json=given - 'summary',
            )
            assert status == '799 Summary Not In Form'

            when(
                'Trying to pass without estimated time',
                json=given - 'estimatedTime',
            )
            assert status == '901 Estimated Time Not In Form'

            when(
                'Estimated time type is wrong',
                json=given | dict(estimatedTime='time'),
            )
            assert status == '900 Invalid Estimated Time Type'

            when(
                'Start date format is wrong',
                json=given | dict(startDate='30-20-20')
            )
            assert status == '791 Invalid Start Date Format'

            when(
                'End date format is wrong',
                json=given | dict(endDate='30-20-20')
            )
            assert status == '790 Invalid End Date Format'

            when(
                'End date must be greater than start date',
                json=given | dict(
                    startDate=form['endDate'],
                    endDate=form['startDate'],
                )
            )
            assert status == '657 End Date Must Be Greater Than Start Date'

            when('Start date is null', json=given | dict(startDate=None))
            assert status == '905 Start Date Is Null'

            when('End date is null', json=given | dict(endDate=None))
            assert status == '906 End Date Is Null'

            when('Estimated time is null', json=given | dict(estimatedTime=None))
            assert status == '904 Estimated Time Is Null'

            when('Summary is null', json=given | dict(summary=None))
            assert status == '903 Summary Is Null'

            when('Request is not authorized', authorization=None)
            assert status == 401

