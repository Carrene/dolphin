from auditing.middleware import MiddleWareFactory
from auditing.context import Context
from nanohttp import context

from dolphin import dolphin as app


def callback(audit_log):
    print(f'verb: {audit_log[0].verb}')
    print(f'status: {audit_log[0].status}')


app.configure()
app.initialize_orm()
middleware = MiddleWareFactory(callback)
app = middleware(app)

