from datetime import datetime

from nanohttp import json, context
from nanohttp.exceptions import HTTPForbidden, HTTPStatus
from restfulpy.orm import DBSession, commit
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from sqlalchemy import and_

from ..models import Activity, Member, Phase, Item
from ..validators import DATETIME_PATTERN, iso_to_datetime


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
    @Activity.validate(
        strict=True,
        fields=dict(
            start_time=dict(
                type_=(iso_to_datetime, '771 Invalid startTime Format')
            ),
            end_time=dict(
                type_=(iso_to_datetime, '772 Invalid endTime Format')
            ),
            description=dict(
                max_length=(256, '773 Invalid description Format')
            )
        )
    )
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
        start_time = form.get('start_time', None)
        end_time = form.get('end_time', None)
        description = form.get('description', '')

        if start_time and end_time:
            if start_time >= end_time:
                raise HTTPStatus('640 endTime Must be Greater Than startTime')

        activity = Activity(
            item=item,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        DBSession.add(activity)
        return activity
