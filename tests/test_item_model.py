from datetime import datetime, timedelta

from nanohttp import settings
from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.testing import db
from auditor.context import Context as AuditLogContext

from dolphin.models import Item, Project, Member, Workflow, Group, Release, \
    Specialty, Phase, Issue, Dailyreport, IssuePhase


def test_item_perspective(db):
    with AuditLogContext(dict()):
        session = db()
        session.expire_on_commit = True

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            reference_id=3,
        )
        session.add(member2)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
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

        with Context(dict()):
            context.identity = member1

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
                specialty=specialty,
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
                start_date=datetime.now().date() - timedelta(days=2),
                end_date=datetime.now().date(),
            )
            session.add(item)
            session.commit()

            assert item.perspective == 'overdue'

            dailyreport1 = Dailyreport(
                date=datetime.now().date() - timedelta(days=2),
                hours=3,
                note='The note for a daily report 1',
                item=item,
            )
            session.add(dailyreport1)
            session.commit()

            assert item.perspective == 'overdue'

            dailyreport2 = Dailyreport(
                date=datetime.now().date() - timedelta(days=1),
                hours=3,
                item=item,
                note='The note for a daily report 2',
            )
            session.add(dailyreport2)
            session.commit()

            assert item.perspective == 'due'

            dailyreport3 = Dailyreport(
                date=datetime.now().date(),
                item=item,
                hours=1,
                note='The note for a daily report 3',
            )
            session.add(dailyreport3)
            session.commit()

            assert item.perspective == 'submitted'

            item1 = Item(
                issue_phase=issue_phase1,
                member_id=member2.id,
                start_date=datetime.now().date() - timedelta(days=2),
                end_date=datetime.now().date() - timedelta(days=1),
            )
            session.add(item1)

            dailyreport4 = Dailyreport(
                date=datetime.now().date() - timedelta(days=2),
                hours=3,
                note='The note for a daily report 1',
                item=item1,
            )
            session.add(dailyreport4)
            session.commit()

            assert item1.perspective == 'overdue'


def test_item_hours_worked(db):
    with AuditLogContext(dict()):
        session = db()
        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            reference_id=1,
        )
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            reference_id=2,
        )
        session.add(member2)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
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

        with Context(dict()):
            context.identity = member1

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
                specialty=specialty,
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
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            reference_id=2,
        )
        session.add(member2)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
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

        with Context(dict()):
            context.identity = member1

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
                specialty=specialty,
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
    session = db()

    with AuditLogContext(dict()):
        member = Member(
            title='First Member',
            email='member@example.com',
            access_token='access token 1',
            phone=111111111,
            reference_id=2
        )
        session.add(member)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
        group = Group(title='Example Group')

        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            specialty=specialty,
        )
        session.add(phase1)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = member

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
                member_id=member.id,
            )
            session.add(item1)
            session.commit()

            assert item1.response_time == None

            item1.need_estimate_timestamp = datetime.now()
            session.commit()
            assert item1.response_time > 0

            item1.need_estimate_timestamp = datetime \
                .strptime('2019-2-2', '%Y-%m-%d')
            session.commit()
            assert item1.response_time < 0


def test_grace_period(db):
    with AuditLogContext(dict()):
        session = db()
        session.expire_on_commit = True

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(member1)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
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

        with Context(dict()):
            context.identity = member1

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
                specialty=specialty,
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
                start_date=datetime.now().date() - timedelta(days=2),
                end_date=datetime.now().date(),
            )
            session.add(item)
            session.commit()

            assert item.grace_period == None

            item.need_estimate_timestamp = datetime.now() - timedelta(days=3)
            session.commit()

            assert item.grace_period > 0

            item.need_estimate_timestamp = datetime.now() - timedelta(days=6)
            session.commit()

            assert item.grace_period < 0


def test_mojo(db):
    with AuditLogContext(dict()):
        session = db()
        session.expire_on_commit = True

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(member1)
        session.commit()

        workflow = Workflow(title='Default')
        specialty = Specialty(title='First Specialty')
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

        with Context(dict()):
            context.identity = member1

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
                specialty=specialty,
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
                start_date=datetime.now().date() - timedelta(days=1),
                end_date=datetime.now().date(),
                estimated_hours=6,
            )
            session.add(item)

            dailyreport1 = Dailyreport(
                date=datetime.now().date() - timedelta(days=1),
                hours=3,
                note='The note for a daily report 1',
                item=item,
            )
            session.add(dailyreport1)
            session.commit()

            assert item.mojo_remaining_hours == 3
            assert item.mojo_progress == 50
            assert item._days_left_to_estimate == 1
            assert item.mojo_boarding == 'on-time'

            dailyreport1.hours = 0
            session.commit()
            assert item.mojo_boarding == 'at-risk'

            item.start_date = item.start_date - timedelta(days=1)
            dailyreport2 = Dailyreport(
                date=datetime.now().date() - timedelta(days=2),
                hours=4,
                note='The note for a daily report 2',
                item=item,
            )
            session.add(dailyreport2)

            item.estimated_hours = 15
            dailyreport1.hours = 5
            session.commit()

            assert item.mojo_boarding == 'delayed'

