from datetime import datetime

from nanohttp import settings
from restfulpy.testing import db
from auditor.context import Context as AuditLogContext

from dolphin import Dolphin
from dolphin.models import Member, Workflow, Skill, Group, Phase, Release, \
    Project, Issue, Item


def test_response_time(db):
    settings.merge(
    '''
        item:
          response_time: 48
    '''
    )

    with AuditLogContext(dict()):
        session = db()
        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

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
            room_id=1
        )

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=3
        )
        session.add(issue2)
        session.flush()

        item1 = Item(
            issue_id=issue1.id,
            phase_id=phase1.id,
            member_id=member1.id,
            status='done',
        )
        session.add(item1)

        item2 = Item(
            issue_id=issue2.id,
            phase_id=phase1.id,
            member_id=member1.id,
        )
        session.add(item2)
        session.commit()

    assert item2.response_time.total_seconds() > 0

    assert item1.response_time == None

    item1.status = 'in-progress'
    settings.item.response_time = 0.00000001
    assert item1.response_time.total_seconds() < 0

    settings.item.response_time = 1
    assert item1.response_time.total_seconds() > 0

