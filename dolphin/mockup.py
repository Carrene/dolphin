from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.orm import DBSession
from sqlalchemy_media import StoreManager

from .models import Resource, Phase, Member, Organization, OrganizationMember, \
    Skill, Workflow


def insert(): # pragma: no cover
    # These mockup datas are shared between panda and dolphin.
    # The GOD id is 1.

    skill = DBSession.query(Skill) \
        .filter(Skill.title == 'Project Manager') \
        .one()

    workflow = DBSession.query(Workflow) \
        .filter(Workflow.title == 'Default') \
        .one()

    phase1 = Phase(
        title='First Phase',
        order=1,
        workflow_id=workflow.id,
        skill_id=skill.id,
    )
    phase2 = Phase(
        title='Second Phase',
        order=2,
        workflow_id=workflow.id,
        skill_id=skill.id,
    )

    with Context(dict()), StoreManager(DBSession):
        god = DBSession.query(Member).filter(Member.title == 'GOD').one()

        class Identity:
            id = god.id
            email = god.email

        context.identity = Identity

        organization = DBSession.query(Organization) \
            .filter(Organization.title == 'carrene') \
            .one()
        phase = DBSession.query(Phase).filter(Phase.title == 'Backlog').one()

        resource1 = Resource(
            id=2,
            title='User_1',
            email='user1@example.com',
            skill_id=skill.id,
            password=123456,
        )
        DBSession.add(resource1)
        DBSession.flush()

        organization_resource1 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource1.id,
            role='member',
        )
        DBSession.add(organization_resource1)

        resource2 = Resource(
            id=3,
            title='User_2',
            email='user2@example.com',
            skill_id=skill.id,
            password=123456,
        )
        DBSession.add(resource2)
        DBSession.flush()

        organization_resource2 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource2.id,
            role='member',
        )
        DBSession.add(organization_resource2)

        resource3 = Resource(
            id=4,
            title='User_3',
            email='user3@example.com',
            skill_id=skill.id,
            password=123456,
        )
        DBSession.add(resource3)
        DBSession.flush()

        organization_resource3 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource3.id,
            role='member',
        )
        DBSession.add(organization_resource3)
        DBSession.commit()

        print('Following resource has been added:')
        print(resource1)
        print(resource2)
        print(resource3)

