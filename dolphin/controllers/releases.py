from nanohttp import text, RestController
from restfulpy.controllers import RootController


class ReleaseController(RootController):

    @text
    def index(self):
        from .. import __version__ as version
        return version


