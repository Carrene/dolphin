import contextlib
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPStatus, HTTPServer
from mimetypes import guess_type
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from restfulpy.application import Application
from restfulpy.helpers import copy_stream
from restfulpy.messaging import Messenger


SERVER_LOCK = threading.Event()


@contextlib.contextmanager
def mockup_http_server(app=None, handler_class=WSGIRequestHandler,
                server_class=WSGIServer, bind=('', 0)):
    server = server_class(bind, handler_class)
    if app:
        assert isinstance(server, WSGIServer)
        server.set_app(app)

    thread = threading.Thread(
        target=server.serve_forever,
        name='sa-media test server.',
        daemon=True
    )
    thread.start()
    url = 'http://localhost:%s' % server.server_address[1]
    yield server, url
    server.shutdown()
    thread.join()


def mockup_http_static_server(content: bytes = b'Simple file content.',
                              content_type: str = None, **kwargs):
    class StaticMockupHandler(BaseHTTPRequestHandler):  # pragma: no cover
        def serve_text(self):
            self.send_header('Content-Type', "text/plain")
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Last-Modified', self.date_time_string())
            self.end_headers()
            self.wfile.write(content)

        def serve_static_file(self, filename):
            self.send_header('Content-Type', guess_type(filename))
            with open(filename, 'rb') as f:
                self.serve_stream(f)

        def serve_stream(self, stream):
            buffer = io.BytesIO()
            self.send_header(
                'Content-Length',
                str(copy_stream(stream, buffer))
            )
            self.end_headers()
            buffer.seek(0)
            try:
                copy_stream(buffer, self.wfile)

            except ConnectionResetError:
                pass

        def do_GET(self):
            self.send_response(HTTPStatus.OK)
            if isinstance(content, bytes):
                self.serve_text()

            elif isinstance(content, str):
                self.serve_static_file(content)

            else:
                self.send_header('Content-Type', content_type)
                self.serve_stream(content)

    return simple_http_server(
        None,
        handler_class=StaticMockupHandler,
        server_class=HTTPServer,
        **kwargs
    )


class MockupMessenger(Messenger):
    _last_message = None

    @property
    def last_message(self):
        return self.__class__._last_message

    @last_message.setter
    def last_message(self, value):
        self.__class__._last_message = value

    def send(
            self,
            to, subject, body,
            cc=None,
            bcc=None,
            template_string=None,
            template_filename=None,
            from_=None,
            attachments=None
    ):
        if attachments:
            for attachment in attachments:
                assert hasattr(attachment, 'name')

        self.last_message = {
            'to': to,
            'body': body,
            'subject': subject
        }


class MockupApplication(Application):
    __configuration__ = '''
     db:
       url: postgresql://postgres:postgres@localhost/restfulpy_dev
       test_url: postgresql://postgres:postgres@localhost/restfulpy_test
       administrative_url: postgresql://postgres:postgres@localhost/postgres
    '''

