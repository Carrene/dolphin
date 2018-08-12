from os.path import dirname, join

from restfulpy import Application

from .controllers.root import Root
from .models import Subscribable, Member, Project, Release, Issue, Tag,\
    Stage, Manager, Resource, Guest, Team, Item
from . import mockup


__version__ = '0.1.0-planning.0'


class Dolphin(Application):

    __configuration__ = '''
      db:
        url: postgresql://postgres:postgres@localhost/dolphin_dev
        test_url: postgresql://postgres:postgres@localhost/dolphin_test
        administrative_url: postgresql://postgres:postgres@localhost/postgres
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

