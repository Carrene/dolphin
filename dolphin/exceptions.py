from nanohttp import HTTPKnownStatus


class StatusRoomMemberAlreadyExist(HTTPKnownStatus):
    status = '604 Already Added To Target'


class StatusRoomMemberNotFound(HTTPKnownStatus):
    status = '611 User Not Found'


class StatusChatServerNotFound(HTTPKnownStatus):
    status = '617 Chat Server Not Found'


class StatusChatRoomNotFound(HTTPKnownStatus):
    status = '618 Chat Room Not Found'


class StatusChatServerNotAvailable(HTTPKnownStatus):
    status = '800 Chat Server Not Available'


class StatusChatInternallError(HTTPKnownStatus):
    status = '801 Chat Server Internal Error'


class StatusOutOfLimitRoomSubscription(HTTPKnownStatus):
    status = '804 Number Of Chat Room Subscription Is Out Of Limit'


class StatusCASServerNotFound(HTTPKnownStatus):
    status = '619 CAS Server Not Found'


class StatusCASServerNotAvailable(HTTPKnownStatus):
    status = '802 CAS Server Not Available'


class StatusCASServerInternalError(HTTPKnownStatus):
    status = '803 CAS Server Internall Error'


class StatusInvalidApplicationID(HTTPKnownStatus):
    status = '620 Invalid Application ID'


class StatusInvalidSecret(HTTPKnownStatus):
    status = '621 Invalid Secret'


class StatusRepetitiveTitle(HTTPKnownStatus):
    status = '600 Repetitive Title'


class StatusTokenExpired(HTTPKnownStatus):
    status = '627 Token Expired'


class StatusMalformedToken(HTTPKnownStatus):
    status = '626 Malformed Token'


class StatusAlreadyInThisOrganization(HTTPKnownStatus):
    status = '628 Already In This Organization'


class StatusAlreadyTagAdded(HTTPKnownStatus):
    status = '634 Already Tag Added'


class StatusAlreadyTagRemoved(HTTPKnownStatus):
    status = '635 Already Tag Removed'


class StatusNotSubscribedIssue(HTTPKnownStatus):
    status = '637 Not Subscribed Issue'


class StatusRelatedIssueNotFound(HTTPKnownStatus):
    def __init__(self, related_issue_id):
        self.status = f'647 relatedIssue With Id {related_issue_id} Not Found'


class StatusResourceNotFound(HTTPKnownStatus):

    def __init__(self, resource_id):
        self.status = f'609 Resource not found with id: {resource_id}'


class StatusIssueBugMustHaveRelatedIssue(HTTPKnownStatus):
    status = '649 The Issue Bug Must Have A Related Issue'


class StatusManagerNotFound(HTTPKnownStatus):
    status = '608 Manager Not Found'


class StatusSecondaryManagerNotFound(HTTPKnownStatus):
    status = '650 Secondary Manager Not Found'


class StatusLaunchDateMustGreaterThanCutoffDate(HTTPKnownStatus):
    status = '651 The Launch Date Must Greater Than Cutoff Date'


class StatusIssueNotFound(HTTPKnownStatus):
    status = '605 Issue Not Found'


class StatusMemberNotFound(HTTPKnownStatus):
    status = '610 Member Not Found'


class StatusAlreadyAddedToGroup(HTTPKnownStatus):
    status = '652 Already Added To Group'


class StatusMemberNotExistsInGroup(HTTPKnownStatus):
    status = '653 Member Not Exists In Group'


class StatusAlreadyGrantedSkill(HTTPKnownStatus):
    status = '655 Skill Already Granted'


class StatusSkillNotGrantedYet(HTTPKnownStatus):
    status = '656 Skill Not Granted Yet'


class StatusRepetitiveOrder(HTTPKnownStatus):
    status = '615 Repetitive Order'


class StatusSkillNotFound(HTTPKnownStatus):
    status = '645 Skill Not Found'


class StatusGroupNotFound(HTTPKnownStatus):
    status = '659 Group Not Found'


class StatusEventTypeNotFound(HTTPKnownStatus):
    status = '658 Event Type Not Found'


class StatusEndDateMustBeGreaterThanStartDate(HTTPKnownStatus):
    status = '657 End Date Must Be Greater Than Start Date'


class StatusInvalidStartDateFormat(HTTPKnownStatus):
    status = '791 Invalid Start Date Format'


class StatusInvalidEndDateFormat(HTTPKnownStatus):
    status = '790 Invalid End Date Format'


class StatusLimitedCharecterForSummary(HTTPKnownStatus):
    status = '902 At Most 1024 Characters Are Valid For Summary'


class StatusInvalidEstimatedTimeType(HTTPKnownStatus):
    status = '900 Invalid Estimated Time Type'


class StatusSummaryNotInForm(HTTPKnownStatus):
    status = '799 Summary Not In Form'


class StatusStartDateNotInForm(HTTPKnownStatus):
    status = '792 Start Date Not In Form'


class StatusEndDateNotInForm(HTTPKnownStatus):
    status = '793 End Date Not In Form'


class StatusEstimatedTimeNotInForm(HTTPKnownStatus):
    status = '901 Estimated Time Not In Form'


class StatusSummaryIsNull(HTTPKnownStatus):
    status = '903 Summary Is Null'


class StatusEstimatedTimeIsNull(HTTPKnownStatus):
    status = '904 Estimated Time Is Null'


class StatusStartDateIsNull(HTTPKnownStatus):
    status = '905 Start Date Is Null'


class StatusEndDateIsNull(HTTPKnownStatus):
    status = '906 End Date Is Null'


class StatusRepeatNotInForm(HTTPKnownStatus):
    status = '911 Repeat Not In Form'


class StatusQueryParameterNotInFormOrQueryString(HTTPKnownStatus):
    status = '912 Query Parameter Not In Form Or Query String'

