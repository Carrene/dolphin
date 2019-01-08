from nanohttp import context
from nanohttp.contexts import Context
from restfulpy.orm import DBSession
from sqlalchemy_media import StoreManager

from .models import Resource, Phase, Member


def indented(n): # pragma: no cover
    def decorator(f):
        def wrapper(*a, **kw):
            for i in f(*a, **kw):
                print(f'{n*" "}{i}')
            print()
        return wrapper
    return decorator


@indented(2)
def print_resource(m): # pragma: no cover
    yield f'title: {m.title}'
    yield f'email: {m.email}'


def insert(): # pragma: no cover
    # These mockup datas are shared between panda and dolphin.
    # The GOD id is 1.

    with Context(dict()), StoreManager(DBSession):
        god = DBSession.query(Member).filter(Member.title == 'GOD').one()

        class Identity:
            id = god.id
            email = god.email

        context.identity = Identity

        phase = DBSession.query(Phase).filter(Phase.title == 'Backlog').one()

        resource1 = Resource(
            id=2,
            title='User_1',
            email='user1@example.com',
            reference_id=2,
            access_token='access token 2',
            phase=phase,
        )
        DBSession.add(resource1)

        resource2 = Resource(
            id=3,
            title='User_2',
            email='user2@example.com',
            reference_id=3,
            access_token='access token 3',
            phase=phase,
        )
        DBSession.add(resource2)

        resource3 = Resource(
            id=4,
            title='User_3',
            email='user3@example.com',
            reference_id=4,
            access_token='access token 4',
            phase=phase,
        )
        DBSession.add(resource3)
        DBSession.commit()

        print('Following resource has been added:')
        print_resource(resource1)
        print_resource(resource2)
        print_resource(resource3)

