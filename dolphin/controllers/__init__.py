from nanohttp import text
from restfulpy.controllers import RootController


class Root(RootController):

    @text
    def index(self):
        from .. import __version__ as version
        return version
