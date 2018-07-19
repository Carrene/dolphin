from nanohttp import Controller, json, text
from restfulpy.controllers import RootController

import dolphin


class Apiv1(Controller):

   @json
   def version(self):
       return dict(version=dolphin.__version__)


class Root(RootController):

    apiv1 = Apiv1()

    @text
    def index(self):
        return 'Dolphin is working well\n'

