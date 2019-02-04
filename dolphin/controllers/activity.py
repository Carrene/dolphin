from datetime import datetime

from nanohttp import json, context, validate, int_or_notfound
from nanohttp.exceptions import HTTPForbidden, HTTPStatus, HTTPNotFound
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
        form = context.form
        start_time = form.get('startTime', None)
        end_time = form.get('endTime', None)
        description = form.get('description', '')

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

        self.check_times(start_time, end_time)

        activity = Activity(
            item=item,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        DBSession.add(activity)
        return activity

    @authorize
    @Activity.validate(strict=False)
    @json(prevent_empty_form='708 Empty Form')
    @Activity.expose
    @commit
    def update(self, id):
        id = int_or_notfound(id)

        form = context.form
        start_time = form.get('startTime', None)
        end_time = form.get('endTime', None)
        self.check_times(start_time, end_time)

        activity = DBSession.query(Activity).get(id)
        member = Member.current()

        if activity is None or activity.item.member_id != member.id:
            raise HTTPNotFound()

        activity.update_from_request()
        return activity

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Activity.expose
    def list(self):
        member = Member.current()
        return DBSession.query(Activity) \
            .join(Item, Item.id == Activity.item_id) \
            .filter(Item.issue_id == self.issue.id, Item.member_id == member.id)


    def check_times(self, start_time, end_time):
        if start_time and end_time:
            if start_time >= end_time:
                raise HTTPStatus('640 endTime Must be Greater Than startTime')

        if start_time and start_time > datetime.utcnow():
            raise HTTPStatus('642 startTime Must Be Smaller Than Current Time')

        if end_time and end_time > datetime.utcnow():
            raise HTTPStatus('643 endTime Must Be Smaller Than Current Time')

