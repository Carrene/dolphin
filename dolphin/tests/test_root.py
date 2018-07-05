
import pytest

from restfulpy.configuration import configure
from nanohttp import settings
from restfulpy.orm import DBSession
from restfulpy.testing import WebAppTestCase

class DatabaseManager:

    def __init__(self, configuration):
        self.configure(configuration)
        self.prepare_database()

    def prepare_database(self):
        with DatabaseManager() as m:
            m.drop_database()
            m.create_database()

        cls.engine = create_engine()
        cls.session = session = session_factory(
            bind=cls.engine,
            expire_on_commit=False
        )
        setup_schema(session)
        session.commit()

    def configure(self, configuration):
        configure(configuration)
        settings.db.url = settings.db.test_url

    def connect(self) -> 'Session':
        raise NotImplementedError()

    def drop_database(self):
        raise NotImplementedError()

    def create_database(self):
        raise NotImplementedError()

    def create_schema(self):
        raise NotImplementedError()

    def insert_basedata(self):
        raise NotImplementedError()


@pytest.fixture
def db():
    configure()
    print('Initializing DB')

    builtin_configuration = '''
	db:
      test_url: postgresql://postgres:postgres@localhost/dolphin_test
      administrative_url: postgresql://postgresql:postgres@localhost/postgres
    '''

    database_manager = DatabaseManager(builtin_configuration)
    return DatabaseManager
    print('Teardown the DB')


def test_db(db):
    database = db('''

    ''')
    with database.connect() as session:
        assert session.query(Person).count() == 23



