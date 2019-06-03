from datetime import datetime

from auditor.context import Context as AuditLogContext
from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.testing import db

from dolphin.models import Item, Project, Member, Workflow, Group, Release, Skill, Phase, Issue


def test_item_perspective(db):
    session = db()

    with AuditLogContext(dict()):
        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member)

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

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
                status='in-progress',
                kind='feature',
                days=1,
                room_id=2,
            )
            session.add(issue1)

            issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                status='to-do',
                kind='feature',
                days=2,
                room_id=3,
            )
            session.add(issue2)

            phase1 = Phase(
                workflow=workflow,
                title='Backlog',
                order=1,
                skill=skill,
            )
            session.add(phase1)

            phase2 = Phase(
                workflow=workflow,
                title='Test',
                order=2,
                skill=skill
            )
            session.add(phase1)

            phase3 = Phase(
                workflow=workflow,
                title='Development',
                order=3,
                skill=skill
            )
            session.add(phase1)
            session.flush()

            item1 = Item(
                issue_id=issue1.id,
                phase_id=phase1.id,
                member_id=member.id,
                start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
                estimated_hours=4,
            )
            session.add(item1)

            item2 = Item(
                issue_id=issue1.id,
                phase_id=phase2.id,
                member_id=member.id,
                start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
                estimated_hours=4,
            )
            session.add(item2)

            item3 = Item(
                issue_id=issue1.id,
                phase_id=phase3.id,
                member_id=member.id,
                start_date=datetime.strptime('2019-2-2', '%Y-%m-%d'),
                end_date=datetime.strptime('2019-2-3', '%Y-%m-%d'),
                estimated_hours=4,
            )
            session.add(item3)
            session.commit()

    assert issue1.due_date == item3.end_date
    assert issue2.due_date == None

