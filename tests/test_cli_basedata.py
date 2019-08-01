import base64
import json

from bddcli import Given, given, when, stdout, stderr, Application, status
from restfulpy import Application as RestfulpyApplication
from restfulpy.testing import db

from dolphin import dolphin
from dolphin.models import Member


foo = RestfulpyApplication(name='jwt')


def foo_main():
    import pudb; pudb.set_trace()  # XXX BREAKPOINT
    return dolphin.cli_main()


app = Application('dolphin', 'tests.test_cli_basedata:foo_main')


def test_jwt(db):
    session = db()
    with Given(app, 'db create --drop --basedata'):
        import pudb; pudb.set_trace()  # XXX BREAKPOINT
        assert status == 0
        assert len(stdout) > 10
        god = session.query(Member).get(1)

        when(given + '\'{"foo": 1}\'')
        assert stderr == ''
        assert status == 0
        header, payload, signature = stdout.encode().split(b'.')
        payload = base64.urlsafe_b64decode(payload)
        assert json.loads(payload) == {'foo': 1}


if __name__ == '__main__':  # pragma: no cover
    import pudb; pudb.set_trace()  # XXX BREAKPOINT
    foo.cli_main(['db', 'create', '--drop', '--basedata'])

