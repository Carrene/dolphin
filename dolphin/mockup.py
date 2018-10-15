from restfulpy.orm import DBSession

from .models import Release


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
    DBSession.commit()

    print('Following releases have been added:')
    print_subscribables(release1)
    print_subscribables(release2)
    print_subscribables(release3)
    print_subscribables(release4)
    print_subscribables(release5)

