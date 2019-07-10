from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy import and_

from ..exceptions import StatusIssueIdIsNull, StatusInvalidIssueIdType, \
    StatusIssueIdNotInForm, StatusIssueNotFound, StatusInvalidBatch
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
        ),
    ))
    @commit
    def append(self, title):
        issue_id = context.form['issueIds']
        issue = DBSession.query(Issue) \
            .filter(Issue.id == issue_id) \
            .one_or_none()

        if issue is None:
            raise StatusIssueNotFound(issue_id)

        title = int_or_notfound(title)
        batch = DBSession.query(Batch) \
            .filter(and_(
                Batch.title == format(title, '03'),
                Batch.project_id == issue.project_id
            )) \
            .one_or_none()

        lastbatch = DBSession.query(Batch) \
            .filter(Batch.project_id == issue.project_id) \
            .order_by(Batch.id.desc()) \
            .first()

        if batch is None:
            for i in range(title - int(lastbatch.title)):
                batch_title = int(lastbatch.title) + i + 1
                if batch_title < 100:
                    batch = Batch(title=format(batch_title, '03'))
                    batch.project_id = issue.project_id
                    DBSession.add(batch)

                else:
                    raise StatusInvalidBatch

            batch.issues.append(issue)

        else:
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
            raise StatusIssueNotFound()

        issue.batch_id = None
        return batch

