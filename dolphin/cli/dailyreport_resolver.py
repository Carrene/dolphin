from datetime import datetime

from easycli import SubCommand
from restfulpy.orm import DBSession, commit

from ..models import Dailyreport, Item, Event


class FixWeekendSubCommand(SubCommand):  # pragma: no cover
    __help__ = 'Fills daily report of weekends(Fridays).'
    __command__ = 'fix-weekend'
    __arguments__ = []

    def __call__(self, args):
        for item in DBSession.query(Item) \
                .filter(Item.estimated_hours != None) \
                .filter(Item.start_date < datetime.now()) \
                .filter(Item.end_date > datetime.now()):

            dailyreport = Dailyreport(
                note='',
                hours=0,
                item_id=item.id,
                date=datetime.now().date(),
            )
            DBSession.add(dailyreport)

        DBSession.commit()


class FixEventSubCommand(SubCommand):  # pragma: no cover
    __help__ = 'Fills daily report of events.'
    __command__ = 'fix-event'
    __arguments__ = []

    def __call__(self, args):
        is_today_event = DBSession.query(Event) \
            .filter(Event.start_date < datetime.now()) \
            .filter(Event.end_date > datetime.now()) \
            .first()

        if is_today_event is not None:
            for item in DBSession.query(Item) \
                    .filter(Item.estimated_hours != None) \
                    .filter(Item.start_date < datetime.now()) \
                    .filter(Item.end_date > datetime.now()):

                dailyreport = Dailyreport(
                    note='',
                    hours=0,
                    item_id=item.id,
                    date=datetime.now().date(),
                )
                DBSession.add(dailyreport)

            DBSession.commit()

