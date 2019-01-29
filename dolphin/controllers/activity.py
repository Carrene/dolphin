from nanohttp import json, context
from sqlalchemy import and_

from nanohttp.exceptions import HTTPForbidden
from restfulpy.orm import DBSession, commit
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController

from ..models import Activity, Member, Phase, Item


def int_or_false(arg):
    try:
        return int(arg)
    except (TypeError, ValueError):
        return False


class ActivityController(ModelRestController):
    __model__ = Activity

    def __init__(self, issue=None):
        self.issue = issue

    @authorize
    @Activity.validate(strict=True)
    @json
    @Activity.expose
    @commit
    def create(self):

        member = Member.current()

        item = DBSession.query(Item) \
            .filter(
                and_(
                    Item.member_id == member.id,
                    Item.issue_id == self.issue.id
                )
            ) \
            .order_by(Item.created_at.desc()) \
            .first()

        if item is None:
            raise HTTPForbidden()

        form = context.form
        start_time = getattr(form, 'starTime', None)
        end_time = getattr(form, 'endTime', None)
        description = getattr(form, 'description', '')

        activity = Activity(
            item=item,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        DBSession.add(activity)
        return activity

