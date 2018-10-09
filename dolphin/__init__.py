from os.path import dirname, join

from restfulpy import Application

from .authentication import Authenticator
from .controllers.root import Root
from . import mockup


__version__ = '0.8.0'


class Dolphin(Application):
    __authenticator__ = Authenticator()
    __configuration__ = '''
      db:
        url: postgresql://postgres:postgres@localhost/dolphin_dev
        test_url: postgresql://postgres:postgres@localhost/dolphin_test
        administrative_url: postgresql://postgres:postgres@localhost/postgres

      oauth:

        secret: A1dFVpz4w/qyym+HeXKWYmm6Ocj4X5ZNv1JQ7kgHBEk=\n
        application_id: 1
        url: http://localhost:8081

      chat:
        url: http://localhost:8082

   '''

    def __init__(self, application_name='dolphin', root=Root()):
        super().__init__(
            application_name,
            root=root,
            root_path=join(dirname(__file__), '..'),
            version=__version__
        )

    def insert_mockup(self, *args):
        mockup.insert()


dolphin = Dolphin()

