from os.path import dirname, join

from restfulpy import Application

from .authentication import Authenticator
from .controllers.root import Root
from . import basedata


__version__ = '0.12.3nightly'


class Dolphin(Application):
    __authenticator__ = Authenticator()
    __configuration__ = '''
      db:
        url: postgresql://postgres:postgres@localhost/dolphin_dev
        test_url: postgresql://postgres:postgres@localhost/dolphin_test
        administrative_url: postgresql://postgres:postgres@localhost/postgres

      migration:
        directory: %(root_path)s/migration
        ini: %(root_path)s/alembic.ini

      logging:
        loggers:
          backends:
            propagate: false
            level: debug
            handlers:
              - backend_handler

        handlers:
          backend_handler:
            type: file
            filename: /tmp/dolphin-backends.log

      oauth:
        secret: A1dFVpz4w/qyym+HeXKWYmm6Ocj4X5ZNv1JQ7kgHBEk=\n
        application_id: 1
        url: http://localhost:8080

      chat:
        url: http://localhost:8081

   '''

    def __init__(self, application_name='dolphin', root=Root()):
        super().__init__(
            application_name,
            root=root,
            root_path=join(dirname(__file__), '..'),
            version=__version__
        )

    def insert_basedata(self, *args):
        basedata.insert()


dolphin = Dolphin()

