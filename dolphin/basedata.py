from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.orm import DBSession
from sqlalchemy_media import StoreManager

from .models import Release, Admin, Organization, OrganizationMember,\
    Workflow, Phase, Tag, Group, Specialty, EventType


def insert(): # pragma: no cover

    default_workflow = Workflow(title='Default')

    public_group = Group(title='Public', public=True)
    DBSession.add(public_group)

    specialty = Specialty(title='Project Manager')

    phase1 = Phase(
        title='Design',
        order=1,
        workflow=default_workflow,
        specialty=specialty
    )
    DBSession.add(phase1)

    phase2 = Phase(
        title='Development',
        order=2,
        workflow=default_workflow,
        specialty=specialty
    )
    DBSession.add(phase2)

    phase3 = Phase(
        title='Test',
        order=3,
        workflow=default_workflow,
        specialty=specialty
    )
    DBSession.add(phase3)

    event_type1 = EventType(
        title='Personal',
    )
    DBSession.add(event_type1)

    event_type2 = EventType(
        title='Company-Wide',
    )
    DBSession.add(event_type2)
    DBSession.commit()

    with Context(dict()), StoreManager(DBSession):
        god = Admin(
            id=1,
            title='GOD',
            email='god@example.com',
            access_token='access token 1',
            reference_id=1
        )
        DBSession.add(god)
        DBSession.flush()

        class Identity:
            email = god.email
            id = god.id

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

        print('Following tags have been added:')
        print(code_review_tag)
        print(database_tag)
        print(documentation_tag)

        print('Following event-type has been added:')
        print(event_type1)
        print(event_type2)

        print('Following group has been added:')
        print(public_group)

