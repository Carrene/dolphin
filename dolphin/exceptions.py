from nanohttp import HTTPKnownStatus


class ChatServerNotFound(HTTPKnownStatus):
    status = '617 Chat Server Not Found'


class ChatServerNotAvailable(HTTPKnownStatus):
    status = '800 Chat Server Not Available'


class ChatInternallError(HTTPKnownStatus):
    status = '801 Chat Server Internal Error'

