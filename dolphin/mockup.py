from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.orm import DBSession
from sqlalchemy_media import StoreManager

from .models import Resource, Member, Organization, OrganizationMember, \
    Specialty


def insert(): # pragma: no cover
    # These mockup datas are shared between panda and dolphin.
    # The GOD id is 1.

    specialty = DBSession.query(Specialty) \
        .filter(Specialty.title == 'front-end') \
        .one()

    with Context(dict()), StoreManager(DBSession):
        god = DBSession.query(Member).filter(Member.title == 'GOD').one()

        class Identity:
            id = god.id
            email = god.email

        context.identity = Identity

        organization = DBSession.query(Organization) \
            .filter(Organization.title == 'carrene') \
            .one()

        resource1 = Resource(
            id=2,
            title='User_1',
            email='user1@example.com',
            reference_id=2,
            access_token='access token 2',
            specialty_id=specialty.id,
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
            reference_id=3,
            access_token='access token 3',
            specialty_id=specialty.id,
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
            reference_id=4,
            access_token='access token 4',
            specialty_id=specialty.id,
        )
        DBSession.add(resource3)
        DBSession.flush()

        organization_resource3 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource3.id,
            role='member',
        )
        DBSession.add(organization_resource3)

        resource4 = Resource(
            id=5,
            title='User_4',
            email='user4@example.com',
            reference_id=5,
            access_token='access token 5',
            specialty_id=specialty.id,
        )
        DBSession.add(resource4)
        DBSession.flush()

        organization_resource4 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource4.id,
            role='member',
        )
        DBSession.add(organization_resource4)

        resource5 = Resource(
            id=6,
            title='User_5',
            email='user5@example.com',
            reference_id=6,
            access_token='access token 6',
            specialty_id=specialty.id,
        )
        DBSession.add(resource5)
        DBSession.flush()

        organization_resource5 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource5.id,
            role='member',
        )
        DBSession.add(organization_resource5)

        resource6 = Resource(
            id=7,
            title='User_6',
            email='user6@example.com',
            reference_id=7,
            access_token='access token 7',
            specialty_id=specialty.id,
        )
        DBSession.add(resource6)
        DBSession.flush()

        organization_resource6 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource6.id,
            role='member',
        )
        DBSession.add(organization_resource6)

        resource7 = Resource(
            id=8,
            title='User_7',
            email='user7@example.com',
            reference_id=8,
            access_token='access token 8',
            specialty_id=specialty.id,
        )
        DBSession.add(resource7)
        DBSession.flush()

        organization_resource7 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource7.id,
            role='member',
        )
        DBSession.add(organization_resource7)

        resource8 = Resource(
            id=9,
            title='User_8',
            email='user8@example.com',
            reference_id=9,
            access_token='access token 8',
            specialty_id=specialty.id,
        )
        DBSession.add(resource8)
        DBSession.flush()

        organization_resource8 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource8.id,
            role='member',
        )
        DBSession.add(organization_resource8)

        resource9 = Resource(
            id=10,
            title='User_9',
            email='user9@example.com',
            reference_id=10,
            access_token='access token 10',
            specialty_id=specialty.id,
        )
        DBSession.add(resource9)
        DBSession.flush()

        organization_resource9 = OrganizationMember(
            organization_id=organization.id,
            member_id=resource9.id,
            role='member',
        )
        DBSession.add(organization_resource9)
        DBSession.commit()

        print('Following resource has been added:')
        print(resource1)
        print(resource2)
        print(resource3)
        print(resource4)
        print(resource5)
        print(resource6)
        print(resource7)
        print(resource8)
        print(resource9)

