from nanohttp import HTTPKnownStatus


class RoomMemberAlreadyExist(HTTPKnownStatus):
    status = '604 Already Added To Target'


class RoomMemberNotFound(HTTPKnownStatus):
    status = '611 User Not Found'


class ChatServerNotFound(HTTPKnownStatus):
    status = '617 Chat Server Not Found'


class ChatRoomNotFound(HTTPKnownStatus):
    status = '618 Chat Room Not Found'


class ChatServerNotAvailable(HTTPKnownStatus):
    status = '800 Chat Server Not Available'


class ChatInternallError(HTTPKnownStatus):
    status = '801 Chat Server Internal Error'

