from auditor import context as AuditLogContext
from nanohttp import HTTPStatus, json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..backends import ChatClient
from ..exceptions import StatusChatRoomNotFound, \
    StatusRoomMemberAlreadyExist, StatusRoomMemberNotFound, \
    StatusManagerNotFound, StatusSecondaryManagerNotFound
from ..models import Batch, Project, Member, Subscription, Workflow, Group, Release
from ..validators import project_validator, update_project_validator
from .files import FileController
from .issues import IssueController


class BatchController(ModelRestController):
    __model__ = Batch

    @authorize
    @json
    @Batch_validator
    @Batch.expose
    @commit
    def append(self):
        issues = context.form['issueId']
        batch= Batch()

        last_batch = DBSession.query(Batch) \
            .filter(Batch.max(Batch.id)) \
            .one()

        if last_batch:
            DBSession.add(batch)

        batch.update_from_request()
        DBSession.add(batch)

        return batch




