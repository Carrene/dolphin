from datetime import datetime, timedelta

from bddrest import status, response, when, Update
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Skill, Phase, Release, \
    Project, Issue, Item
from dolphin.tests.helpers import create_group, LocalApplicationTestCase, \
    oauth_mockup_server, create_workflow


class TestActivity(LocalApplicationTestCase):

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

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            phone=1234567890,
            password='123ABCabc',
        )

        workflow = create_workflow()
        skill = Skill(title='First Skill')

        cls.phase1 = Phase(
            title='Backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(cls.phase1)

        phase2 = Phase(
            title='PreBacklog',
            order=-2,
            workflow=workflow,
            skill=skill,
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

        cls.issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue2)
        session.flush()

        old_item = Item(
            issue_id=cls.issue1.id,
            phase_id=phase2.id,
            member_id=cls.member.id,
        )
        session.add(old_item)

        cls.item = Item(
            issue_id=cls.issue1.id,
            phase_id=cls.phase1.id,
            member_id=cls.member.id,
        )
        session.add(cls.item)

        cls.item_for_someone_else = Item(
            issue_id=cls.issue2.id,
            phase_id=cls.phase1.id,
            member_id=member2.id,
        )
        session.add(cls.item)

        session.commit()

    def test_create(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Creating an activity',
            f'/apiv1/issues/id: {self.issue1.id}/activities',
            f'CREATE',
            form=dict(
                startTime=(
                    datetime.utcnow() - timedelta(minutes=1)
                ).isoformat(),
                endTime=datetime.utcnow().isoformat(),
                description='I worked for 1 minute',
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['item']['id'] == self.item.id
            assert response.json['description'] is not None
            assert response.json['startTime'] is not None
            assert response.json['endTime'] is not None
            assert response.json['createdAt'] is not None
            assert response.json['modifiedAt'] is None
            assert response.json['timeSpan'] == 60

            when(
                'startTime, endTime and description Is None',
                form={}
            )
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['item']['id'] == self.item.id
            assert response.json['description'] == ''
            assert response.json['startTime'] is None
            assert response.json['endTime'] is None
            assert response.json['timeSpan'] is None

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
                'Create Activity For Unassign Issue',
                url_parameters=Update(id=self.issue2.id)
            )
            assert status == 403

            when(
                'Issue Not Found',
                url_parameters=Update(id=0)
            )
            assert status == 404
