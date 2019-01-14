from auditing import MiddleWareFactory

from dolphin import dolphin as app


def callback(audit_log):
    print(f'verb: {audit_log[0].verb}')
    print(f'status: {audit_log[0].status}')


app.configure()
app.initialize_orm()
middleware = MiddleWareFactory(callback)
app = middleware(app)

