from restfulpy.orm import DBSession

from .models import Member, Project


def insert(): # pragma: no cover
    member1 = Member(
        title='First Member',
        email='member1@example.com',
        access_token='access token 1',
        phone=123456789,
        reference_id=2
    )

    project1 = Project(
        member=member1,
        title='My first project',
        description='A decription for my project',
        room_id=1001
    )
    DBSession.add(project1)
    DBSession.commit()

