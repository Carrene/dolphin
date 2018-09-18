from contextlib import contextmanager

from nanohttp import settings, RegexRouteController, json
from restfulpy.mockup import mockup_http_server

from dolphin.tests.helpers import MockupApplication, LocalApplicationTestCase


@contextmanager
def jaguar_mockup_server():
    class Root(RegexRouteController):
        def __init__(self):
            super().__init__([
                ('/apiv1/rooms', self.create),
            ])

        @json
        def create(self):
            return dict(room_id=1)

    app = MockupApplication('jaguar-server', Root())
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            tokenizer:
              url: {url}
        ''')
        yield app

class TestMockup(LocalApplicationTestCase):

    def test_mockup_server(self):
        with jaguar_mockup_server():
            import pudb; pudb.set_trace()  # XXX BREAKPOINT
            print('hello')
