from os import path

from restfulpy.application import Application
from restfulpy.testing import ApplicableTestCase

from dolphin import Dolphin
from dolphin.authentication import Authenticator


HERE = path.abspath(path.dirname(__file__))
DATA_DIRECTORY = path.abspath(path.join(HERE, '../../data'))


class LocalApplicationTestCase(ApplicableTestCase):
    __application_factory__ = Dolphin
    __story_directory__ = path.join(DATA_DIRECTORY, 'stories')
    __api_documentation_directory__ = path.join(DATA_DIRECTORY, 'markdown')


class MockupApplication(Application):

    def __init__(self, application_name, root):
        super().__init__(
            application_name,
            root=root
        )
        self.__authenticator__ = Authorization()


class Authorization(Authenticator):

    def validate_credentials(self, credentials):
        pass

    def create_refresh_principal(self, member_id=None):
        pass

    def create_principal(self, member_id=None, session_id=None, **kwargs):
        pass

    def authenticate_request(self):
        pass

