from datetime import datetime

from nanohttp import settings
from restfulpy.testing import db
from auditor.context import Context as AuditLogContext

from dolphin.models import Item, Project, Member, Workflow, Group, Release, \
    Skill, Phase, Issue, Dailyreport, IssuePhase


def test_issue_phase(db):
    with AuditLogContext(dict()):
        session = db()
        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(member1)

        workflow = Workflow(title='Default')
        session.add(workflow)

        skill = Skill(title='First Skill')
        session.add(skill)

        group = Group(title='default')
        session.add(group)

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )
        session.add(release)

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1,
        )
        session.add(project)

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

        issue_phase = IssuePhase(
            issue_id=issue1.id,
            phase_id=phase1.id,
        )
        session.add(issue_phase)
        session.flush()

        item = Item(
            issue_phase_id=issue_phase.id,
            member_id=member1.id,
        )
        session.add(item)
        session.commit()

        dailyreport1 = Dailyreport(
            date=datetime.strptime('2019-1-2', '%Y-%m-%d').date(),
            hours=3,
            note='The note for a daily report',
            item=item,
        )
        session.add(dailyreport1)
        session.commit()

        assert issue_phase.status == 'to-do'

        dailyreport2 = Dailyreport(
            date=datetime.strptime('2019-1-3', '%Y-%m-%d').date(),
            hours=3,
            item=item,
        )
        session.add(dailyreport2)
        session.commit()

