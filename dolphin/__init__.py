from os.path import dirname, join
import functools

from nanohttp import settings
from restfulpy import Application
from sqlalchemy_media import StoreManager, FileSystemStore

from . import basedata
from .authentication import Authenticator
from .cli.email import EmailLauncher
from .controllers.root import Root


__version__ = '0.14.0nightly'


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

      organization_invitation:
        secret: !!binary xxSN/uarj5SpcEphAHhmsab8Ql2Og/2IcieNfQ3PysI=
        max_age: 86400  # seconds
        algorithm: HS256
        callback_url: http://localhost:8082

      messaging:
        default_messenger: restfulpy.messaging.ConsoleMessenger
        template_dirs:
          - %(root_path)s/email_templates

      storage:
        local_directory: %(root_path)s/data/assets
        base_url: http://localhost:8080/assets
   '''

    def __init__(self, application_name='dolphin', root=Root()):
        super().__init__(
            application_name,
            root=root,
            root_path=dirname(__file__),
            version=__version__
        )

    def insert_basedata(self, *args):
        basedata.insert()

    @classmethod
    def initialize_orm(cls, engine=None):
        StoreManager.register(
            'fs',
            functools.partial(
                FileSystemStore,
                settings.storage.local_directory,
                base_url=settings.storage.base_url,
            ),
            default=True
        )
        super().initialize_orm(cls, engine)


dolphin = Dolphin()

