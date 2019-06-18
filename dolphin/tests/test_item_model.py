from datetime import datetime

from nanohttp import settings
from restfulpy.testing import db
from auditor.context import Context as AuditLogContext

from dolphin.models import Item, Project, Member, Workflow, Group, Release, \
    Skill, Phase, Issue, Dailyreport, IssuePhase


def test_item_perspective(db):
    with AuditLogContext(dict()):
        session = db()
        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')
        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )
        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1,
        )
        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2,
        )
        session.add(issue1)
        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase1)
        session.flush()

        issue_phase1 = IssuePhase(
            issue_id=issue1.id,
            phase_id=phase1.id,
        )

        item = Item(
            issue_phase=issue_phase1,
            member_id=member1.id,
        )
        session.add(item)
        session.commit()

        assert item.perspective == 'Due'

        dailyreport1 = Dailyreport(
            date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
            hours=3,
            note='The note for a daily report',
            item=item,
        )
        session.add(dailyreport1)
        session.commit()

        dailyreport2 = Dailyreport(
            date=datetime.strptime('2019-1-3', '%Y-%m-%d').date(),
            hours=3,
            item=item,
        )
        session.add(dailyreport2)
        session.commit()

        assert item.perspective == 'Overdue'

        dailyreport2.note = 'The note for a daily report'
        session.commit()

        assert item.perspective == 'Submitted'

        dailyreport3 = Dailyreport(
            date=datetime.now().date(),
            hours=3,
            item=item,
        )
        session.add(dailyreport3)
        session.commit()

        assert item.perspective == 'Due'

        dailyreport3.note = 'The note for a daily report'
        session.commit()

        assert item.perspective == 'Submitted'


def test_item_hours_worked(db):
    with AuditLogContext(dict()):
        session = db()
        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            reference_id=1,
        )
        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            reference_id=2,
        )
        session.add(member2)

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')
        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )
        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1,
        )
        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2,
        )
        session.add(issue1)
        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase1)
        session.flush()

        issue_phase1 = IssuePhase(
            issue_id=issue1.id,
            phase_id=phase1.id,
        )

        item1 = Item(
            issue_phase=issue_phase1,
            member_id=member1.id,
            estimated_hours=4
        )
        session.add(item1)
        session.commit()

        item2 = Item(
            issue_phase=issue_phase1,
            member_id=member2.id,
            estimated_hours=4
        )
        session.add(item2)
        session.commit()

        assert item1.hours_worked == None
        assert item2.hours_worked == None

        dailyreport1 = Dailyreport(
            date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
            hours=3,
            note='The note for a daily report',
            item=item1,
        )
        session.add(dailyreport1)
        session.commit()

        assert item1.hours_worked == 3
        assert item2.hours_worked == None

        dailyreport2 = Dailyreport(
            date=datetime.strptime('2019-1-3', '%Y-%m-%d').date(),
            hours=3,
            item=item1,
        )
        session.add(dailyreport2)
        session.commit()

        assert item1.hours_worked == 6
        assert item2.hours_worked == None


def test_item_status(db):
    with AuditLogContext(dict()):
        session = db()
        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            reference_id=1,
        )
        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            reference_id=2,
        )
        session.add(member2)

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')
        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )
        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1,
        )
        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2,
        )
        session.add(issue1)
        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase1)
        session.flush()

        issue_phase1 = IssuePhase(
            issue_id=issue1.id,
            phase_id=phase1.id,
        )

        item1 = Item(
            issue_phase=issue_phase1,
            member_id=member1.id,
            estimated_hours=4
        )
        session.add(item1)
        session.commit()

        item2 = Item(
            issue_phase=issue_phase1,
            member_id=member2.id,
            estimated_hours=4
        )
        session.add(item2)
        session.commit()

        assert item1.status == 'to-do'

        dailyreport1 = Dailyreport(
            date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
            hours=3,
            note='The note for a daily report',
            item=item1,
        )
        session.add(dailyreport1)
        session.commit()

        assert item1.status == 'in-progress'

        dailyreport2 = Dailyreport(
            date=datetime.strptime('2019-1-3', '%Y-%m-%d').date(),
            hours=3,
            item=item1,
        )
        session.add(dailyreport2)
        session.commit()

        assert item1.status == 'complete'


def test_response_time(db):
    settings.merge(
        '''
            item:
              response_time: 48
        '''
    )

    with AuditLogContext(dict()):
        session = db()
        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=111111111,
            reference_id=3
        )

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='Example Group')

        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase1)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member2,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member2,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            kind='feature',
            days=1,
            room_id=3
        )
        session.add(issue2)
        session.flush()

        issue_phase1 = IssuePhase(
            issue_id=issue1.id,
            phase_id=phase1.id,
        )

        item1 = Item(
            issue_phase=issue_phase1,
            member_id=member2.id,
        )
        session.add(item1)

        issue_phase2 = IssuePhase(
            issue_id=issue2.id,
            phase_id=phase1.id,
        )

        item2 = Item(
            issue_phase=issue_phase2,
            member_id=member2.id,
        )
        session.add(item2)
        session.commit()

    assert item2.response_time.total_seconds() > 0

#    assert item1.response_time == None

#    item1.status = 'in-progress'
#    settings.item.response_time = 0.0000000001
#    assert item1.response_time.total_seconds() < 0
#
#    settings.item.response_time = 1
#    assert item1.response_time.total_seconds() > 0

