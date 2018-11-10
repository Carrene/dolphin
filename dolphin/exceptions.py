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


class CASServerNotFound(HTTPKnownStatus):
    status = '619 CAS Server Not Found'


class CASServerNotAvailable(HTTPKnownStatus):
    status = '802 CAS Server Not Available'


class CASServerInternalError(HTTPKnownStatus):
    status = '803 CAS Server Internall Error'


class InvalidApplicationID(HTTPKnownStatus):
    status = '620 Invalid Application ID'


class InvalidSecret(HTTPKnownStatus):
    status = '621 Invalid Secret'

