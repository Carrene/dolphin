from datetime import datetime, timedelta

from restfulpy.testing import db
from auditor.context import Context as AuditLogContext
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Item, Project, Member, Workflow, Group, Release, \
    Specialty, Phase, Issue, Dailyreport, IssuePhase, Skill


def test_status(db):
    with AuditLogContext(dict()):
        session = db()
        session.expire_on_commit = True

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            reference_id=2,
        )
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 1',
            reference_id=3,
        )
        session.add(member2)
        session.commit()

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
        )

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

            issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=4,
            )
            session.add(issue2)

            phase1 = Phase(
                title='des',
                order=-1,
                workflow=workflow,
                specialty=specialty,
            )
            session.add(phase1)
            session.flush()

            phase2 = Phase(
                title='back',
                order=-1,
                workflow=workflow,
                specialty=specialty,
            )
            session.add(phase2)
            session.flush()

            phase3 = Phase(
                title='front',
                order=-1,
                workflow=workflow,
                specialty=specialty,
            )
            session.add(phase3)
            session.flush()

            issue_phase1 = IssuePhase(
                issue_id=issue1.id,
                phase_id=phase1.id,
            )
            session.add(issue_phase1)
            session.flush()

            item1 = Item(
                issue_phase_id=issue_phase1.id,
                member_id=member1.id,
                start_date=datetime.strptime('2019-1-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2019-2-2', '%Y-%m-%d'),
                estimated_hours=5,
            )
            session.add(item1)
            session.flush()

            item2 = Item(
                issue_phase_id=issue_phase1.id,
                member_id=member2.id,
                start_date=datetime.strptime('2019-1-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2019-2-2', '%Y-%m-%d'),
                estimated_hours=6,
            )
            session.add(item2)
            session.flush()

            issue_phase2 = IssuePhase(
                issue_id=issue1.id,
                phase_id=phase2.id,
            )
            session.add(issue_phase2)
            session.flush()

            item3 = Item(
                issue_phase_id=issue_phase2.id,
                member_id=member1.id,
                start_date=datetime.strptime('2019-1-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2019-2-2', '%Y-%m-%d'),
                estimated_hours=5,
            )
            session.add(item1)
            session.commit()

        assert issue_phase1.status == 'to-do'

        dailyreport1 = Dailyreport(
            date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
            hours=3,
            note='The note for a daily report',
            item=item1,
        )
        session.add(dailyreport1)
        session.commit()

        assert issue_phase1.status == 'in-progress'

        dailyreport2 = Dailyreport(
            date=datetime.strptime('2019-1-3', '%Y-%m-%d').date(),
            hours=3,
            note='The note for a daily report',
            item_id=item1.id,
        )
        session.add(dailyreport2)
        session.commit()

        assert issue_phase1.status == 'to-do'

        dailyreport3 = Dailyreport(
            date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
            hours=7,
            note='The note for a daily report',
            item=item2,
        )
        session.add(dailyreport3)

        dailyreport4 = Dailyreport(
            date=datetime.strptime('2019-1-3', '%Y-%m-%d').date(),
            hours=5,
            note='The note for a daily report',
            item_id=item2.id,
        )
        session.add(dailyreport4)
        session.commit()

        assert issue_phase1.status == 'complete'


def test_mojo(db):
    with AuditLogContext(dict()):
        session = db()
        session.expire_on_commit = True

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            reference_id=2,
        )
        session.add(member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 1',
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

            issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=4,
            )
            session.add(issue2)

            phase1 = Phase(
                title='des',
                order=-1,
                workflow=workflow,
                specialty=specialty,
            )
            session.add(phase1)
            session.flush()

            phase2 = Phase(
                title='back',
                order=-1,
                workflow=workflow,
                specialty=specialty,
            )
            session.add(phase2)
            session.flush()

            phase3 = Phase(
                title='front',
                order=-1,
                workflow=workflow,
                specialty=specialty,
            )
            session.add(phase3)
            session.flush()

            issue_phase1 = IssuePhase(
                issue_id=issue1.id,
                phase_id=phase1.id,
            )
            session.add(issue_phase1)
            session.flush()

            item1 = Item(
                issue_phase_id=issue_phase1.id,
                member_id=member1.id,
                start_date=datetime.now() - timedelta(days=2),
                end_date=datetime.now(),
                estimated_hours=4,
            )
            session.add(item1)
            session.flush()

            item2 = Item(
                issue_phase_id=issue_phase1.id,
                member_id=member2.id,
                start_date=datetime.now() - timedelta(days=2),
                end_date=datetime.now(),
                estimated_hours=6,
            )
            session.add(item2)

            dailyreport1 = Dailyreport(
                date=datetime.now().date(),
                hours=5,
                note='The note for a daily report',
                item=item1,
            )
            session.add(dailyreport1)
            session.commit()

            assert issue_phase1.mojo_remaining_hours == 5
            assert issue_phase1.mojo_progress == 50
            assert issue_phase1._days_left_to_estimate == 5
            assert issue_phase1.mojo_boarding == 'on-time'

            item1.estimated_hours = 22
            item1.start_date = datetime.now() - timedelta(days=5)

            item2.estimated_hours = 25
            item2.start_date = datetime.now() - timedelta(days=5)

            dailyreport2 = Dailyreport(
                date=datetime.now().date() - timedelta(days=1),
                hours=3,
                note='The note for a daily report',
                item=item1,
            )
            session.add(dailyreport2)

            dailyreport3 = Dailyreport(
                date=datetime.now().date(),
                hours=5,
                note='The note for a daily report',
                item=item2,
            )
            session.add(dailyreport3)

            dailyreport4 = Dailyreport(
                date=datetime.now().date() - timedelta(days=1),
                hours=2,
                note='The note for a daily report',
                item=item2,
            )
            session.add(dailyreport4)
            session.commit()

            assert issue_phase1.mojo_boarding == 'delayed'

            dailyreport1.hours = 1
            dailyreport2.hours = 1
            dailyreport3.hours = 1
            dailyreport4.hours = 1
            session.commit()

            assert issue_phase1.mojo_boarding == 'at-risk'

