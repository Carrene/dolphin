from os.path import dirname, join
import functools

from nanohttp import settings
from restfulpy import Application
from sqlalchemy_media import StoreManager, FileSystemStore

from . import basedata, mockup
from .authentication import Authenticator
from .cli import EmailSubCommand
from .controllers.root import Root


__version__ = '0.46.2a9'


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

      issue:
        subscription:
          max_length: 100

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

      attachments:
        files:
          max_length: 50 # KB
          min_length: 1  # KB
        organizations:
          logos:
            max_length: 50 # KB
            min_length: 1  # KB
        applications:
          icons:
            max_length: 50 # KB
            min_length: 1  # KB
        members:
          avatars:
            max_length: 50 # KB
            min_length: 1  # KB

      item:
        response_time: 48 # Hours

      resource:
        load_thresholds:
          heavy: 5
          medium: 3

      reset_password:
        secret: !!binary xxSN/uarj5SpcEphAHhmsab8Ql2Og/2IcieNfQ3PysI=
        max_age: 3600  # seconds
        algorithm: HS256
        callback_url: http://localhost:8083

      registration:
        secret: !!binary xxSN/uarj5SpcEphAHhmsab8Ql2Og/2IcieNfQ3PysI=
        max_age: 86400  # seconds
        algorithm: HS256
        callback_url: http://localhost:8083

      authorization_code:
        secret: !!binary T8xNMJCFl4xgBSW3NaDv6/D+48ssBWZTQbqqDlnl0gU=
        max_age: 86400  # seconds
        algorithm: HS256

      access_token:
        secret: !!binary dKcWy4fQTpgjjAhS6SbapQUvtxPhiO23GguaV9U1y7k=
        max_age: 2592000  # seconds
        algorithm: HS256

      smtp:
        host: smtp.gmail.com
        username: cas@carrene.com
        password: <password>
        local_hostname: carrene.com

      sms:
        provider: panda.sms.ConsoleSmsProvider
        cm:
          sender: cas@Carrene
          refrence: Carrene
          token: <token>
          url: https://gw.cmtelecom.com/v1.0/message
        kavenegar:
          apiKey: <key>

      phone:
        activation_token:
          secret: !!binary dKcWy4fQTpgjjAhS6SbapQUvtxPhiO23GguaV9U1y7k=
          max_age: 360  # seconds
          algorithm: HS256
        activation_code:
          length: 6
          hash_algorithm: SHA-1
          time_interval: 59 # seconds
          challenge_limit: 40
          seed: !!python/bytes 8QYEd+yEh4fcZ5aAVqrlXBWuToeXTyOeHFun8OzOL48=
          window: 4
        jwt:
          max_age: 86400

      organization_invitation:
        secret: !!binary dKcWy4fQTpgjjAhS6SbapQUvtxPhiO23GguaV9U1y7k=
        max_age: 2592000  # seconds
        algorithm: HS256
        callback_url: http://localhost:8083

   '''

    def __init__(self, application_name='dolphin', root=Root()):
        super().__init__(
            application_name,
            root=root,
            root_path=dirname(__file__),
            version=__version__
        )

    def insert_basedata(self, *args):# pragma: no cover
        basedata.insert()

    def insert_mockup(self, *args):# pragma: no cover
        mockup.insert()

    def get_cli_arguments(self):
        return [
            EmailSubCommand,
        ]

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

