from nanohttp import HTTPKnownStatus


class RoomMemberAlreadyExist(HTTPKnownStatus):
    statu = '604 Already Added To Target'


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


class OutOfLimitRoomSubscription(HTTPKnownStatus):
    status = '804 Number Of Chat Room Subscription Is Out Of Limit'

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


class HTTPRepetitiveTitle(HTTPKnownStatus):
    status = '600 Repetitive Title'


class HTTPTokenExpired(HTTPKnownStatus):
    status = '627 Token Expired'


class HTTPMalformedToken(HTTPKnownStatus):
    status = '626 Malformed Token'


class HTTPAlreadyInThisOrganization(HTTPKnownStatus):
    status = '628 Already In This Organization'


class HTTPAlreadyTagAdded(HTTPKnownStatus):
    status = '634 Already Tag Added'


class HTTPAlreadyTagRemoved(HTTPKnownStatus):
    status = '635 Already Tag Removed'


class HTTPNotSubscribedIssue(HTTPKnownStatus):
    status = '637 Not Subscribed Issue'


class HTTPRelatedIssueNotFound(HTTPKnownStatus):
    def __init__(self, related_issue_id):
        self.status = f'647 relatedIssue With Id {related_issue_id} Not Found'


class HTTPResourceNotFound(HTTPKnownStatus):

    def __init__(self, resource_id):
        self.status = f'609 Resource not found with id: {resource_id}'


class HTTPIssueBugMustHaveRelatedIssue(HTTPKnownStatus):
    status = '649 The Issue Bug Must Have A Related Issue'


class HTTPManagerNotFound(HTTPKnownStatus):
    status = '608 Manager Not Found'


class HTTPSecondaryManagerNotFound(HTTPKnownStatus):
    status = '650 Secondary Manager Not Found'


class HTTPLaunchDateMustGreaterThanCutoffDate(HTTPKnownStatus):
    status = '651 The Launch Date Must Greater Than Cutoff Date'


class HTTPIssueNotFound(HTTPKnownStatus):
    status = '605 Issue Not Found'

