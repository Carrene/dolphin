from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..exceptions import StatusIssueIdIsNull, StatusInvalidIssueIdType, \
    StatusIssueIdNotInForm, StatusIssueNotFound
from ..models import Batch, Issue


class BatchController(ModelRestController):
    __model__ = Batch

    @authorize
    @json
    @Batch.expose
    @Batch.validate(fields=dict(
        issueIds=dict(
            required=StatusIssueIdNotInForm,
            type_=(int, StatusInvalidIssueIdType),
            not_none=StatusIssueIdIsNull,
        )
    ))
    @commit
    def append(self, id_):
        id_ = int_or_notfound(id_)
        batch = DBSession.query(Batch).filter(Batch.id == id_).one_or_none()
        if batch is None:
            raise HTTPNotFound('Batch with id: {id_} was not found')

        issue_id = context.form['issueIds']
        issue = DBSession.query(Issue) \
            .filter(Issue.id == issue_id) \
            .one_or_none()

        if issue is None:
            raise StatusIssueNotFound(issue_id)

        batch.issues.append(issue)

        return batch

    @authorize
    @json
    @Batch.expose
    @Batch.validate(fields=dict(
        issueIds=dict(
            required=StatusIssueIdNotInForm,
            type_=(int, StatusInvalidIssueIdType),
            not_none=StatusIssueIdIsNull,
        )
    ))
    @commit
    def remove(self, id_):
        id_ = int_or_notfound(id_)
        batch = DBSession.query(Batch).get(id_)
        if batch is None:
            raise HTTPNotFound()

        issue = DBSession.query(Issue).get(context.form.get('issueIds'))
        if issue is None:
            raise StatusIsuueNotFound()

        DBSession.delete(issue)
        return batch

