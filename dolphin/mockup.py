
from restfulpy.orm import DBSession, commit

from .models import Subscribable, Member, Project, Release, Issue, Tag,\
    Phase, Manager, Resource, Guest, Team, Item


def insert(): # pragma: no cover
    guest = Guest(
        title='First Guest',
        email=None,
        phone=1234556789
    )
    DBSession.add(guest)

    manager = Manager(
        title='First Manager',
        email=None,
        phone=123456789
    )
    DBSession.add(manager)

    team = Team(
        title='Awesome team'
    )
    DBSession.add(team)

    resource = Resource(
        team=team,
        title='Developer',
        email='dev@example.com',
        phone=987654321
    )
    DBSession.add(resource)

    release = Release(
        title='My first release',
        description='A decription for my release',
        due_date='2020-2-20',
        cutoff='2030-2-20',
    )
    DBSession.add(release)

    project = Project(
        manager=manager,
        releases=release,
        title='My first project',
        description='A decription for my project',
        due_date='2020-2-20',
    )
    DBSession.add(project)

    issue = Issue(
        project=project,
        title='First issue',
        description='This is description of first issue',
        due_date='2020-2-20',
        kind='feature',
        days=1
    )
    DBSession.add(issue)

    phase = Phase(
        project=project,
        title='design',
        order=1,
    )
    DBSession.add(phase)

    tag = Tag(
        title='Acomplish'
    )
    DBSession.add(tag)

    item = Item(
        resource=resource,
        phase=phase,
        issue=issue,
        status='in-progress',
        end='2020-2-2'
    )
    DBSession.add(item)
    DBSession.commit()

