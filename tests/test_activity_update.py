from datetime import datetime, timedelta

from auditor.context import Context as AuditLogContext
from bddrest import status, response, when, Update
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Member, Specialty, Phase, Release, \
    Project, Issue, Item, Activity, IssuePhase, Skill
from .helpers import create_group, LocalApplicationTestCase, \
    oauth_mockup_server, create_workflow


class TestActivity(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=1234567890,
            reference_id=2
        )
        session.add(member2)
        session.commit()

        workflow = create_workflow()
        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
        )

        cls.phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(cls.phase1)

        phase2 = Phase(
            title='PreBacklog',
            order=-2,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(phase2)

        group = create_group()

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

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue2)
            session.flush()

            issue_phase1 = IssuePhase(
                issue_id=cls.issue1.id,
                phase_id=phase2.id,
            )
            session.add(issue_phase1)
            session.flush()

            old_item = Item(
                issue_phase_id=issue_phase1.id,
                member_id=cls.member.id,
            )
            session.add(old_item)

            issue_phase2 = IssuePhase(
                issue_id=cls.issue1.id,
                phase_id=cls.phase1.id,
            )
            session.add(issue_phase2)
            session.flush()

            cls.item = Item(
                issue_phase_id=issue_phase2.id,
                member_id=cls.member.id,
            )
            session.add(cls.item)

            issue_phase3 = IssuePhase(
                issue_id=cls.issue2.id,
                phase_id=cls.phase1.id,
            )
            session.add(issue_phase3)
            session.flush()

            cls.item_for_someone_else = Item(
                issue_phase_id=issue_phase3.id,
                member_id=member2.id,
            )
            session.add(cls.item)

            cls.activity = Activity(
                item=cls.item,
            )
            session.add(cls.activity)

            cls.activity_for_someone_else = Activity(
                item=cls.item_for_someone_else,
            )
            session.add(cls.activity_for_someone_else)
            session.commit()

    def test_update(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Updating an activity',
            f'/apiv1'
                f'/activities/activity_id: {self.activity.id}',
            f'UPDATE',
            form=dict(
                startTime=(
                    datetime.utcnow() - timedelta(minutes=2)
                ).isoformat(),
                endTime=datetime.utcnow().isoformat(),
                description='I worked for 2 minute',
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['item']['id'] == self.item.id
            assert response.json['description'] is not None
            assert response.json['startTime'] is not None
            assert response.json['endTime'] is not None
            assert response.json['createdAt'] is not None
            assert response.json['modifiedAt'] is not None
            assert response.json['timeSpan'] == 120

            when(
                'startTime > endTime',
                form=dict(
                    startTime=(datetime.utcnow() + timedelta(weeks=1))
                        .isoformat(),
                    endTime=datetime.utcnow().isoformat(),
                ),
            )
            assert status == '640 endTime Must be Greater Than startTime'

            when(
                'Invalid startTime Format',
                form=Update(startTime='abcd')
            )
            assert status == '771 Invalid startTime Format'

            when(
                'startTime Is Greater Than Current Time',
                form=Update(
                    startTime=(datetime.utcnow() + timedelta(seconds=1))
                        .isoformat(),
                    endTime=(datetime.utcnow() + timedelta(seconds=3))
                        .isoformat()
                )
            )
            assert status == '642 startTime Must Be Smaller Than Current Time'

            when(
                'endTime Is Greater Than Current Time',
                form=Update(
                    startTime=(datetime.utcnow() - timedelta(seconds=1))
                        .isoformat(),
                    endTime=(datetime.utcnow() + timedelta(seconds=2))
                        .isoformat()
                )
            )
            assert status == '643 endTime Must Be Smaller Than Current Time'

            when(
                'Invalid endTime Format',
                form=Update(endTime='abcd')
            )
            assert status == '772 Invalid endTime Format'

            when(
                'Invalid description Format',
                form=Update(description='1' * 265)
            )
            assert status == '773 Invalid description Format'

            when(
                'Update Activity Of Someone Else',
                url_parameters=Update(
                    activity_id=self.activity_for_someone_else.id
                )
            )
            assert status == 404

            when(
                'Activity Not Found',
                url_parameters=Update(activity_id=0)
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

            when('Updating project with empty form', form=dict())
            assert status == '708 No Parameter Exists In The Form'
