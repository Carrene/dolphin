from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.orm import DBSession
from sqlalchemy_media import StoreManager

from .models import Release, Member, Organization, OrganizationMember,\
    Workflow, Phase


def indented(n): # pragma: no cover
    def decorator(f):
        def wrapper(*a, **kw):
            for i in f(*a, **kw):
                print(f'{n*" "}{i}')
            print()
        return wrapper
    return decorator


@indented(2)
def print_subscribables(s): # pragma: no cover
    yield f'title: {s.title}'


@indented(2)
def print_member(m): # pragma: no cover
    yield f'title: {m.title}'
    yield f'email: {m.email}'


@indented(2)
def print_organization(s): # pragma: no cover
    yield f'title: {s.title}'


@indented(2)
def print_workflow(w): # pragma: no cover
    yield f'title: {w.title}'


@indented(2)
def print_phase(p): # pragma: no cover
    yield f'title: {p.title}'


def insert(): # pragma: no cover

    release1 = Release(
        title='My first release',
        description='This is an awesome product.',
        cutoff='2030-2-20',
    )
    DBSession.add(release1)

    release2 = Release(
        title='My second release',
        description='A decription for my release.',
        cutoff='2022-2-20',
    )
    DBSession.add(release2)

    release3 = Release(
        title='My third release',
        description='One of the most interesting releases.',
        cutoff='2027-2-20',
    )
    DBSession.add(release3)

    release4 = Release(
        title='My fourth release',
        description='A description for fourth release.',
        cutoff='2030-2-20',
    )
    DBSession.add(release4)

    release5 = Release(
        title='My fifth release',
        description='This release has awesome projects.',
        cutoff='2034-2-20',
    )
    DBSession.add(release5)

    default_workflow = Workflow(title='default')

    phase1 = Phase(
        title='backlog',
        order=-1,
        workflow=default_workflow
    )
    DBSession.add(phase1)

    phase2 = Phase(
        title='triage',
        order=0,
        workflow=default_workflow
    )
    DBSession.add(phase2)
    DBSession.commit()

    with Context(dict()), StoreManager(DBSession):
        god = Member(
            title='GOD',
            email='god@example.com',
            access_token='access token 1',
            reference_id=1
        )
        DBSession.add(god)

        class Identity:
            email = god.email

        context.identity = Identity

        organization = Organization(
            title='carrene',
        )
        DBSession.add(organization)
        DBSession.flush()

        organization_member = OrganizationMember(
            organization_id=organization.id,
            member_id=god.id,
            role='owner',
        )
        DBSession.add(organization_member)

        organization.tags.append(Tag(
            title='Code Review'
        ))
        organization.tags.append(Tag(
            title='Database'
        ))
        organization.tags.append(Tag(
            title='Documentation'
        ))
        DBSession.commit()


        print('Following releases have been added:')
        print_subscribables(release1)
        print_subscribables(release2)
        print_subscribables(release3)
        print_subscribables(release4)
        print_subscribables(release5)

        print('Following user has been added:')
        print_member(god)

        print('Following organization has been added:')
        print_organization(organization)

        print('Following workflow have been added:')
        print_workflow(default_workflow)

        print('Following phases have been added:')
        print_phase(phase1)
        print_phase(phase2)
