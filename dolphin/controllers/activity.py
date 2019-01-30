from datetime import datetime

from nanohttp import json, context, validate
from nanohttp.exceptions import HTTPForbidden, HTTPStatus
from restfulpy.orm import DBSession, commit
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from sqlalchemy import and_

from ..models import Activity, Member, Phase, Item
from ..validators import DATETIME_PATTERN, iso_to_datetime


class ActivityController(ModelRestController):
    __model__ = Activity

    def __init__(self, issue=None):
        self.issue = issue

    @authorize
    @Activity.validate(strict=False)
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
        start_time = form.get('startTime', None)
        end_time = form.get('endTime', None)
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
