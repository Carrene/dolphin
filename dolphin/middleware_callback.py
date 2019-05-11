import traceback
from datetime import datetime

import ujson
from auditor.logentry import ChangeAttributeLogEntry, InstantiationLogEntry, \
    AppendLogEntry, RemoveLogEntry, RequestLogEntry
from nanohttp import context, HTTPStatus
from restfulpy.datetimehelpers import format_datetime

from dolphin.backends import ChatClient
from dolphin.models import Member


AUDIT_LOG_MIMETYPE = 'application/x-auditlog'


def callback(audit_log):

    if audit_log[-1].status == '200 OK' and len(audit_log) > 1:
        chat_client = ChatClient()
        member = Member.current()
        for log in audit_log:
            if isinstance(log, ChangeAttributeLogEntry):
                message = dict(
                    action='Update',
                    attribute=log.attribute_label,
                    old=format_datetime(log.old_value) \
                        if isinstance(log.old_value, datetime) else log.old_value,
                    new=format_datetime(log.new_value) \
                        if isinstance(log.new_value, datetime) else log.new_value,
                )

            elif isinstance(log, InstantiationLogEntry):
                message = dict(
                    action='Create',
                    attribute=None,
                    old=None,
                    new=None,
                )

            elif isinstance(log, AppendLogEntry):
                message = dict(
                    action='Append',
                    attribute=log.attribute_label,
                    old=None,
                    new=log.value,
                )

            elif isinstance(log, RemoveLogEntry):
                message = dict(
                    action='Remove',
                    attribute=log.attribute_label,
                    old=log.value,
                    new=None,
                )

            if not isinstance(log, RequestLogEntry):
                try:
                    chat_client.send_message(
                        room_id=log.object_.room_id,
                        body=ujson.dumps(message),
                        mimetype=AUDIT_LOG_MIMETYPE,
                        token=context.environ['HTTP_AUTHORIZATION'],
                        x_access_token=member.access_token,
                    )

                    # This exception passed because after consulting with
                    # Mr.Mardani, decision made: This exception will be
                    # resolved when the dolphin and jaguar merge together
                except HTTPStatus:
                    traceback.print_exc()
                    pass

