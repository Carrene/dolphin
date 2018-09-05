
from restfulpy.orm import DBSession, commit

from .models import Subscribable, Member, Project, Release, Issue, Tag,\
    Phase, Manager, Resource, Guest, Team, Item


def indented(n):
    def decorator(f):
        def wrapper(*a, **kw):
            for i in f(*a, **kw):
                print(f'{n*" "}{i}')
            print()
        return wrapper
    return decorator


@indented(2)
def print_member(m):
    yield f'user: {m.title}'
    yield f'mail: {m.email}'
    yield f'pass: 123456'


@indented(2)
def print_team(t):
    yield f'title: {t.title}'


@indented(2)
def print_subscribables(s):
    yield f'title: {s.title}'


@indented(2)
def print_item(i):
    yield f'This item is created by assigning issue: ' \
        f'"{i.issue.title}" to resource: "{i.resource.title}", in phase: ' \
        f'"{i.phase.title}".'


def insert(): # pragma: no cover
    guest = Guest(
        title='First Guest',
        email='guest1@example.com',
        password='123456',
        phone=1234556789
    )
    DBSession.add(guest)

    manager = Manager(
        title='First Manager',
        email='manager1@example.com',
        password='123456',
        phone=123456789
    )
    DBSession.add(manager)

    team = Team(
        title='Awesome team'
    )
    DBSession.add(team)

    resource = Resource(
        teams=[team],
        title='First resource',
        email='resource1@example.com',
        password='123456',
        phone=987654321
    )
    DBSession.add(resource)

    release1 = Release(
        title='My first release',
        description='This is an awesome product.',
        due_date='2020-2-20',
        cutoff='2030-2-20',
    )
    DBSession.add(release1)

    release2 = Release(
        title='My second release',
        description='A decription for my release.',
        due_date='2018-2-20',
        cutoff='2022-2-20',
    )
    DBSession.add(release2)

    release3 = Release(
        title='My third release',
        description='One of the most interesting releases.',
        due_date='2025-2-20',
        cutoff='2027-2-20',
    )
    DBSession.add(release3)

    release4 = Release(
        title='My fourth release',
        description='A description for fourth release.',
        due_date='2028-2-20',
        cutoff='2030-2-20',
    )
    DBSession.add(release4)

    release5 = Release(
        title='My fifth release',
        description='This release has awesome projects.',
        due_date='2032-2-20',
        cutoff='2034-2-20',
    )
    DBSession.add(release5)


    project1 = Project(
        manager=manager,
        releases=[release1],
        title='My first project',
        description='This is description for my awesome project.',
        due_date='2020-2-20',
        status='active'
    )
    DBSession.add(project1)

    project2 = Project(
        manager=manager,
        releases=[release1],
        title='My second project',
        description='A project for facilating your teamwork.',
        due_date='2018-3-30',
        status='on-hold'
    )
    DBSession.add(project2)

    project3 = Project(
        manager=manager,
        releases=[release1],
        title='My third project',
        description='A project with interesting features.',
        due_date='2024-2-24',
        status='queued'
    )
    DBSession.add(project3)

    project4 = Project(
        manager=manager,
        releases=[release1],
        title='My fourth project',
        description='Description of project.',
        due_date='2028-2-28',
        status='done'
    )
    DBSession.add(project4)

    issue1 = Issue(
        project=project1,
        title='First issue',
        description='This is description of first issue',
        due_date='2020-2-20',
        kind='feature',
        status='in-progress',
        days=1
    )
    DBSession.add(issue1)

    issue2 = Issue(
        project=project1,
        title='Second issue',
        description='This is description of second issue',
        due_date='2020-2-20',
        kind='feature',
        status='on-hold',
        days=2
    )
    DBSession.add(issue2)

    issue3 = Issue(
        project=project1,
        title='Third issue',
        description='This is description of third issue',
        due_date='2020-2-20',
        kind='feature',
        status='delayed',
        days=3
    )
    DBSession.add(issue3)

    issue4 = Issue(
        project=project1,
        title='Fourth issue',
        description='This is description of fourth issue',
        due_date='2020-2-20',
        kind='feature',
        status='done',
        days=4
    )
    DBSession.add(issue4)

    phase = Phase(
        project=project1,
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
        issue=issue1,
        status='in-progress',
        end='2020-2-2'
    )
    DBSession.add(item)
    DBSession.commit()

    print(
        'Following members have been added, you may log-in using '
        '"/apiv1/tokens"'
    )
    print_member(guest)
    print_member(manager)
    print_member(resource)

    print('Following teams have been added:')
    print_team(team)

    print('Following releases have been added:')
    print_subscribables(release1)
    print_subscribables(release2)
    print_subscribables(release3)
    print_subscribables(release4)
    print_subscribables(release5)

    print('Following projects have been added:')
    print_subscribables(project1)
    print_subscribables(project2)
    print_subscribables(project3)
    print_subscribables(project4)

    print('Following issues has been added:')
    print_subscribables(issue1)
    print_subscribables(issue2)
    print_subscribables(issue3)
    print_subscribables(issue4)

    print('Following phases have been added:')
    print_subscribables(phase)

    print('Following tags have been added:')
    print_subscribables(tag)

    print('Following items have been added:')
    print_item(item)

