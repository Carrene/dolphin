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

        # Title is unique in per a project and always is numerical.
        title = int_or_notfound(title)
        batch = DBSession.query(Batch) \
            .filter(Batch.title == format(title, '03')) \
            .filter(Batch.project_id == issue.project_id) \
            .one_or_none()

        last_batch = DBSession.query(Batch) \
            .filter(Batch.project_id == issue.project_id) \
            .order_by(Batch.id.desc()) \
            .first()

        if batch is None:
            for i in range(title - int(last_batch.title)):
                batch_title = int(last_batch.title) + i + 1
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
