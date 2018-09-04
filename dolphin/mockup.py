
from restfulpy.orm import DBSession, commit

from .models import Subscribable, Member, Project, Release, Issue, Tag,\
    Phase, Manager, Resource, Guest, Team, Item


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
        title='Developer',
        email='resource1@example.com',
        password='123456',
        phone=987654321
    )
    DBSession.add(resource)

    release = Release(
        title='My first release',
        description='A decription for my release.',
        due_date='2020-2-20',
        cutoff='2030-2-20',
    )
    DBSession.add(release)

    project1 = Project(
        manager=manager,
        releases=[release],
        title='My first project',
        description='This is description for my awesome project.',
        due_date='2020-2-20',
        status='in-progress'
    )
    DBSession.add(project1)

    project2 = Project(
        manager=manager,
        releases=[release],
        title='My second project',
        description='A project for facilating your teamwork.',
        due_date='2018-3-30',
        status='on-hold'
    )
    DBSession.add(project2)

    project3 = Project(
        manager=manager,
        releases=[release],
        title='My third project',
        description='A project with interesting features.',
        due_date='2024-2-24',
        status='delayed'
    )
    DBSession.add(project3)

    project4 = Project(
        manager=manager,
        releases=[release],
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

    print('# Added following guest role:')
    for key in guest.to_dict():
        print(f'\t{key}: {guest.to_dict()[key]}')

    print('\n# Added following manager role:')
    for key in manager.to_dict():
        print(f'\t{key}: {manager.to_dict()[key]}')

    print('\n# Added following team role:')
    for key in team.to_dict():
        print(f'\t{key}: {resource.to_dict()[key]}')

    print('\n# Added following resource role:')
    for key in resource.to_dict():
        print(f'\t{key}: {resource.to_dict()[key]}')
    print(f'\trelated to team with id: {team.id}')

    print('\n# Added following release entity:')
    for key in release.to_dict():
        print(f'\t{key}: {release.to_dict()[key]}')

    print('\n# Added following projects entity:')
    print('\tproject1')
    for key in project1.to_dict():
        print(f'\t{key}: {project1.to_dict()[key]}')
    print(f'\trelated to release with id: {release.id}')

    print('\n\tproject2')
    for key in project2.to_dict():
        print(f'\t{key}: {project2.to_dict()[key]}')
    print(f'\trelated to release with id: {release.id}')

    print('\n\tproject3')
    for key in project3.to_dict():
        print(f'\t{key}: {project3.to_dict()[key]}')
    print(f'\trelated to release with id: {release.id}')

    print('\n\tproject4')
    for key in project4.to_dict():
        print(f'\t{key}: {project4.to_dict()[key]}')
    print(f'\trelated to release with id: {release.id}')

    print('\n# Added following issues entity:')
    print('\tissue1')
    for key in issue1.to_dict():
        print(f'\t{key}: {issue1.to_dict()[key]}')
    print(f'\trelated to project with id: {project1.id}')

    print('\n\tissue2')
    for key in issue2.to_dict():
        print(f'\t{key}: {issue2.to_dict()[key]}')
    print(f'\trelated to project with id: {project1.id}')

    print('\n\tissue3')
    for key in issue3.to_dict():
        print(f'\t{key}: {issue3.to_dict()[key]}')
    print(f'\trelated to project with id: {project1.id}')

    print('\n\tissue4')
    for key in issue4.to_dict():
        print(f'\t{key}: {issue4.to_dict()[key]}')
    print(f'\trelated to project with id: {project1.id}')

    print('\n# Added following phase entity:')
    for key in phase.to_dict():
        print(f'\t{key}: {phase.to_dict()[key]}')
    print(f'\trelated to project with id: {project1.id}')

    print('\n# Added following tag entity:')
    for key in tag.to_dict():
        print(f'\t{key}: {tag.to_dict()[key]}')

    print('\n# Added following item entity:')
    for key in item.to_dict():
        print(f'\t{key}: {item.to_dict()[key]}')
    print(
        f'\tCreated by assiging resource with id: {resource.id} to issue1 '
        f'with id: {issue1.id} in the phase with id: {phase.id}'
    )

