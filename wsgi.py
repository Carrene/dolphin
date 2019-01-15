from auditing import MiddleWareFactory
from auditing.logentry import ChangeAttributeLogEntry, InstantiationLogEntry
from nanohttp import context

from dolphin import dolphin as app
from dolphin.backends import ChatClient
from dolphin.models import Member


def callback(audit_log):

    if audit_log[-1].status == '200 OK':
        chat_client = ChatClient()
        member = Member.current()

        # FIXME: We will rollback if cannot send a message successfully
        for log in audit_log:
            if isinstance(log, ChangeAttributeLogEntry):
                chat_client.send_message(
                    room_id=log.obj.room_id,
                    body=f'Update the {log.attribute} by {member.title} '
                         f'from {log.old_value} to {log.new_value}.',
                    token=context.environ['HTTP_AUTHORIZATION'],
                    x_access_token=member.access_token,
                )

            elif isinstance(log, InstantiationLogEntry):
                 chat_client.send_message(
                    room_id=log.obj.room_id,
                    body=f'Created by {member.title}.',
                    token=context.environ['HTTP_AUTHORIZATION'],
                    x_access_token=member.access_token,
                )


app.configure()
app.initialize_orm()
middleware = MiddleWareFactory(callback)
app = middleware(app)
