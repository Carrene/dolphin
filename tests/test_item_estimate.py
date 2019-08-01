from datetime import datetime

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, given
from nanohttp import context
from nanohttp.contexts import Context

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Project, Member, Workflow, Group, Release, \
    Specialty, Phase, Issue, Item, IssuePhase, Skill


class TestItem(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session(expire_on_commit=True)

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member1)
        session.commit()

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
        )

        group = Group(title='default')

        phase1 = Phase(
            title='backlog',
            order=1,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(phase1)

        phase2 = Phase(
            title='backlog',
            order=2,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(phase2)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=1,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=2
        )

        with Context(dict()):
            context.identity = cls.member1

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=3
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=1,
                room_id=4
            )
            session.add(cls.issue2)

            issue_phase1 = IssuePhase(
                issue=cls.issue1,
                phase=phase1,
            )

            cls.item1 = Item(
                issue_phase=issue_phase1,
                member=cls.member1,
                need_estimate_timestamp=datetime.now(),
            )
            session.add(cls.item1)

            issue_phase2 = IssuePhase(
                issue=cls.issue1,
                phase=phase2,
            )

            cls.item2 = Item(
                issue_phase=issue_phase2,
                member=cls.member1,
            )
            session.add(cls.item2)
            session.commit()

    def test_estimate(self):
        session = self.create_session()
        self.login(self.member1.email)
        json = dict(
            startDate=datetime.strptime('2019-2-2', '%Y-%m-%d').isoformat(),
            endDate=datetime.strptime('2019-2-3', '%Y-%m-%d').isoformat(),
            estimatedHours=3,
        )

        with oauth_mockup_server(), self.given(
            'Estimating an item',
            f'/apiv1/items/id: {self.item1.id}',
            'ESTIMATE',
            json=json
        ):
            assert status == 200
            assert response.json['id'] == self.item1.id
            assert response.json['estimatedHours'] == json['estimatedHours']
            assert response.json['startDate'] == json['startDate']
            assert response.json['endDate'] == json['endDate']
            assert self.issue1.stage == 'working'
            assert self.issue2.stage == 'triage'
            assert session.query(Item) \
                .filter(Item.id == self.item1.id) \
                .filter(Item.need_estimate_timestamp == None) \
                .one()

            assert session.query(Item) \
                .filter(Item.id == self.item2.id) \
                .filter(Item.need_estimate_timestamp != None) \
                .one()

            when(
                'Intended item with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended item with string type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Form is empty',
                json=dict()
            )
            assert status == '708 Empty Form'

            when(
                'Form parameter is sent with request',
                json=dict(parameter='Invalid form parameter')
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: startDate, endDate, estimatedHours, isDone'

            when(
                'Start date is less than end date',
                json=given | dict(
                    endDate=datetime \
                        .strptime('2019-1-2', '%Y-%m-%d') \
                        .isoformat()
                )
            )
            assert status == '657 End Date Must Be Greater Than Start Date'

            when(
                'Start date is not in form',
                json=given - 'startDate'
            )
            assert status == '792 Start Date Not In Form'

            when(
                'Start date is not in form',
                json=given | dict(startDate=None)
            )
            assert status == '905 Start Date Is Null'

            when(
                'Start date pattern is wrong',
                json=given | dict(startDate='invalid pattern')
            )
            assert status == '791 Invalid Start Date Format'

            when(
                'End date is not in form',
                json=given - 'endDate'
            )
            assert status == '793 End Date Not In Form'

            when(
                'End date is not in form',
                json=given | dict(endDate=None)
            )
            assert status == '906 End Date Is Null'

            when(
                'End date pattern is wrong',
                json=given | dict(endDate='invalid pattern')
            )
            assert status == '790 Invalid End Date Format'

            when(
                'Estimated hours field is not in form',
                json=given - 'estimatedHours'
            )
            assert status == '901 Estimated Hours Not In Form'

            when(
                'Estimated hours is null',
                json=given | dict(estimatedHours=None)
            )
            assert status == '904 Estimated Hours Is Null'

            when(
                'Estimated hours type is wrong',
                json=given | dict(estimatedHours='invalid type')
            )
            assert status == '900 Invalid Estimated Hours Type'

            when('Request is not authorized', authorization=None)
            assert status == 401

