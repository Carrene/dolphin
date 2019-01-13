from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.orm import DBSession
from sqlalchemy_media import StoreManager

from .models import Release, Member, Organization, OrganizationMember,\
    Workflow, Phase, Tag, Group


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

    default_workflow = Workflow(title='Default')

    public_group = Group(title='Public', public=True)
    DBSession.add(public_group)

    phase1 = Phase(
        title='Backlog',
        order=-1,
        workflow=default_workflow
    )
    DBSession.add(phase1)

    phase2 = Phase(
        title='Triage',
        order=0,
        workflow=default_workflow
    )
    DBSession.add(phase2)

    phase3 = Phase(
        title='Design',
        order=1,
        workflow=default_workflow
    )
    DBSession.add(phase3)

    phase4 = Phase(
        title='Development',
        order=2,
        workflow=default_workflow
    )
    DBSession.add(phase4)

    phase5 = Phase(
        title='Test',
        order=3,
        workflow=default_workflow
    )
    DBSession.add(phase5)
    DBSession.commit()

    with Context(dict()), StoreManager(DBSession):
        god = Member(
            id=1,
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

        code_review_tag = Tag(
            title='Code Review'
        )
        organization.tags.append(code_review_tag)

        database_tag = Tag(
            title='Database'
        )
        organization.tags.append(database_tag)

        documentation_tag = Tag(
            title='Documentation'
        )
        organization.tags.append(documentation_tag)
        DBSession.commit()

        print('Following releases have been added:')
        print(release1, )
        print(release2)
        print(release3)
        print(release4)
        print(release5)

        print('Following user has been added:')
        print(god)

        print('Following organization has been added:')
        print(organization)

        print('Following workflow have been added:')
        print(default_workflow)

        print('Following phases have been added:')
        print(phase1)
        print(phase2)
        print(phase3)
        print(phase4)
        print(phase5)

        print('Following tags have been added:')
        print(code_review_tag)
        print(database_tag)
        print(documentation_tag)

        print('Following group has been added:')
        print(public_group)

