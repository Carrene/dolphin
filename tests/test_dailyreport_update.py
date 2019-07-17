from datetime import datetime, timedelta

from bddrest import status, response, when, given
from auditor.context import Context as AuditLogContext
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Member, Dailyreport, Workflow, Specialty, Group, Phase, \
    Release, Project, Issue, Item, IssuePhase
from .helpers import LocalApplicationTestCase, oauth_mockup_server


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
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
        group = Group(title='default')

        phase = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            specialty=specialty,
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

            cls.item = Item(
                issue_phase=issue_phase1,
                member=cls.member,
                start_date=datetime.now().date() - timedelta(days=1),
                end_date=datetime.now().date(),
            )
            session.add(cls.item)

            cls.dailyreport1 = Dailyreport(
                date=datetime.now().date(),
                hours=3,
                note='The note for a daily report',
                item=cls.item,
            )
            session.add(cls.dailyreport1)

            cls.dailyreport2 = Dailyreport(
                date=datetime.now().date() - timedelta(days=1),
                hours=3,
                note='The note for a daily report',
                item=cls.item,
            )
            session.add(cls.dailyreport2)
            session.commit()

    def test_update(self):
        self.login(self.member.email)
        form = dict(
            hours=4.8,
            note='Some note'
        )

        with oauth_mockup_server(), self.given(
            f'Updating a dailyreport',
            f'/apiv1/items/item_id: {self.item.id}'
                f'/dailyreports/id: {self.dailyreport1.id}',
            f'UPDATE',
            json=form,
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['hours'] == form['hours']
            assert response.json['note'] == form['note']

            last_day = datetime.now().date() - timedelta(days=1)
            when(
                'Can not create two daily reports in one day',
                json=given | dict(date=last_day.isoformat())
            )
            assert status == '665 Daily Report Already Exist'

            when('Date format is wrong', json=given | dict(date='30-20-20'))
            assert status == 400

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Intended timecard with string type not found',
                url_parameters=given | dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Invalid parameter is in form',
                json=given | dict(parameter='invalid parameter')
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: hours, note, date'

            when(
                'Note length is less than limit',
                json=given | dict(note=(1024 + 1) * 'a'),
            )
            assert status == '902 At Most 1024 Characters Are Valid For Note'

            when(
                'Hours value type is wrong',
                json=given | dict(hours='a')
            )
            assert status == '915 Invalid Hours Type'

            when(
                'Hours value is negative',
                json=given | dict(hours=-1)
            )
            assert status == '914 Hours Must Be Positive'

            when('Request is not authorized', authorization=None)
            assert status == 401

