from datetime import datetime

import ujson
from auditing.logentry import ChangeAttributeLogEntry, InstantiationLogEntry
from nanohttp import context
from restfulpy.datetimehelpers import format_datetime

from dolphin.backends import ChatClient
from dolphin.models import Member


AUDIT_LOG_MIMETYPE = 'application/x-auditlog'


def callback(audit_log):

    if audit_log[-1].status == '200 OK' and len(audit_log) > 1:
        chat_client = ChatClient()
        member = Member.current()
        # FIXME: We will rollback if cannot send a message successfully
        for log in audit_log:
            if isinstance(log, ChangeAttributeLogEntry):
                message = dict(
                    action='Update',
                    attribute=log.attribute,
                    old=format_datetime(log.old_value) \
                        if isinstance(log.old_value, datetime) else log.old_value,
                    new=format_datetime(log.new_value) \
                        if isinstance(log.new_value, datetime) else log.new_value,
                )
                chat_client.send_message(
                    room_id=log.obj.room_id,
                    body=ujson.dumps(message),
                    mimetype=AUDIT_LOG_MIMETYPE,
                    token=context.environ['HTTP_AUTHORIZATION'],
                    x_access_token=member.access_token,
                )

            elif isinstance(log, InstantiationLogEntry):
                message = dict(
                    action='Create',
                    attribute=None,
                    old=None,
                    new=None,
                )
                chat_client.send_message(
                    room_id=log.obj.room_id,
                    body=ujson.dums(message),
                    mimetype=AUDIT_LOG_MIMETYPE,
                    token=context.environ['HTTP_AUTHORIZATION'],
                    x_access_token=member.access_token,
                )

