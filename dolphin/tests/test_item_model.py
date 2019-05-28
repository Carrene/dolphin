from datetime import datetime

from auditor.context import Context as AuditLogContext
from restfulpy.testing import db

from dolphin.models import Item, Project, Member, Workflow, Group, Release, \
    Skill, Phase, Issue, Dailyreport


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
            due_date=datetime.strptime('2020-2-20', '%Y-%m-%d'),
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

        item = Item(
            issue_id=issue1.id,
            phase_id=phase1.id,
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

