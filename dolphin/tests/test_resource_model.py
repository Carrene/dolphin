from datetime import datetime

from nanohttp import settings
from restfulpy.testing import db
from auditor.context import Context as AuditLogContext

from dolphin.models import Resource, Group, Workflow, Skill, Phase, Release, \
    Project, Issue, Item


def test_resource_load(db):
    settings.merge(
        '''
          resource:
            load_thresholds:
              heavy: 5
              medium: 3
        '''
    )

    session = db()
    with AuditLogContext(dict()):

        resource1 = Resource(
            title='First Resource',
            email='resource1@example.com',
            access_token='access token 1',
            phone=111111111,
            reference_id=1
        )
        session.add(resource1)

        resource2 = Resource(
            title='Second Resource',
            email='resource2@example.com',
            access_token='access token 2',
            phone=222222222,
            reference_id=2
        )
        session.add(resource2)

        resource3 = Resource(
            title='Third Member',
            email='resource3@example.com',
            access_token='access token 3',
            phone=333333333,
            reference_id=3
        )
        session.add(resource3)

        resource4 = Resource(
            title='Fourth Member',
            email='resource4@example.com',
            access_token='access token 4',
            phone=444444444,
            reference_id=4
        )
        session.add(resource4)

        workflow = Workflow(title='Default')
        session.add(workflow)

        skill = Skill(title='First Skill')
        phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill,
        )
        session.add(phase1)

        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=resource1,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=resource1,
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
            room_id=2,
            priority='low',
        )
        session.add(issue1)

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=3,
            priority='normal',
        )
        session.add(issue2)

        issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of third issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=4,
            priority='high',
        )
        session.add(issue3)
        session.flush()

        # Resource 1 assignments
        item1 = Item(
            issue_id=issue1.id,
            phase_id=phase1.id,
            member_id=resource1.id,
        )
        session.add(item1)

        item2 = Item(
            issue_id=issue2.id,
            phase_id=phase1.id,
            member_id=resource1.id,
            start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(item2)

        item3 = Item(
            issue_id=issue3.id,
            phase_id=phase1.id,
            member_id=resource1.id,
            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(item3)

        # Resource 2 assignments
        item4 = Item(
            issue_id=issue1.id,
            phase_id=phase1.id,
            member_id=resource2.id,
            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(item4)

        item5 = Item(
            issue_id=issue2.id,
            phase_id=phase1.id,
            member_id=resource2.id,
            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(item5)

        # Resource 3 assignments
        item6 = Item(
            issue_id=issue2.id,
            phase_id=phase1.id,
            member_id=resource3.id,
            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
            estimated_hours=3,
        )
        session.add(item6)
        session.commit()

    assert resource1.load == 'heavy'
    assert resource2.load == 'medium'
    assert resource3.load == 'light'
    assert resource4.load == None

