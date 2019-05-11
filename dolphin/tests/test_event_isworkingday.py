from datetime import datetime, timedelta

from dolphin.tests.helpers import db
from dolphin.models import Event, EventType


def test_isworkingday(db):
    session = db()
    one_day = timedelta(days=1)
    two_day = timedelta(days=2)

    event_type = EventType(
        title='First type',
    )

    event1 = Event(
        title='First event',
        start_date=(datetime.now() - one_day).isoformat(),
        end_date=datetime.now().isoformat(),
        event_type=event_type,
        repeat='never',
    )
    session.add(event1)

    event2 = Event(
        title='Second event',
        start_date=datetime.now().isoformat(),
        end_date=(datetime.now() + one_day).isoformat(),
        event_type=event_type,
        repeat='never',
    )
    session.add(event2)
    session.commit()

    is_workingday = Event.isworkingday(session=session)
    assert is_workingday == False

    is_workingday = Event.isworkingday(
        session=session,
        date=datetime.now().date() + one_day
    )
    assert is_workingday == False

    is_workingday = Event.isworkingday(
        session=session,
        date=datetime.now().date() + two_day
    )
    assert is_workingday == True

