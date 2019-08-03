from bddcli import Given, given, when, stdout, Application, status
from nanohttp import settings
from restfulpy.db import PostgreSQLManager as DBManager

from dolphin import dolphin


def foo_main():
    return dolphin.cli_main()


app = Application('dolphin', 'tests.test_cli_basedata:foo_main')


class TestDatabaseAdministrationCommandLine:
    db = None

    @classmethod
    def setup_class(cls):
        dolphin.configure(force=True)
        cls.db = DBManager(settings.db.url)
        cls.db.__enter__()

    @classmethod
    def teardown_class(cls):
        cls.db.__exit__(None, None, None)

    def test_db(self):
        self.db.drop_database()
        assert not self.db.database_exists()

        with Given(app, 'db create --drop --basedata'):
            assert status == 0
            assert len(stdout) > 10
            with self.db.cursor('SELECT * FROM member') as c:
                members = c.fetchall()
                assert len(members) == 1
                assert members[0][8] == 'GOD'

            with self.db.cursor('SELECT * FROM skill') as c:
                skills = c.fetchall()
                assert len(skills) == 1

            with self.db.cursor('SELECT * FROM tag') as c:
                tags = c.fetchall()
                assert len(tags) == 3

            with self.db.cursor('SELECT * FROM phase') as c:
                phases = c.fetchall()
                assert len(phases) == 3

            when(given + '--mockup')
            with self.db.cursor('SELECT * FROM member') as c:
                assert len(c.fetchall()) == 10


if __name__ == '__main__':  # pragma: no cover
    dolphin.cli_main(['db', 'create', '--drop', '--basedata'])

