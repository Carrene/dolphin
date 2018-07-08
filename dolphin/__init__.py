from os.path import dirname, join

from restfulpy import Application

from .controllers import Root


__version__ = '0.1.0-planning.0'

dependencies = [
    'restfulpy',
    'sqlalchemy',
    'nanohttp',

    #Deployment
    'gunicorn',

    #Testing
    'bddrest',
    'pytest'
]

class Dolphin(Application):

    builtin_configuration = '''
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

dolphin = Dolphin()

