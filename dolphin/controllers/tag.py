from nanohttp import json, context, HTTPNotFound, HTTPForbidden
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy import and_, exists

from ..exceptions import HTTPAlreadyTagAdded, HTTPAlreadyTagRemoved
from ..models import Tag, DraftIssueTag, IssueTag


class TagController(ModelRestController):
    __model__ = Tag

    def __init__(self, draft_issue=None, issue=None):
        self.draft_issue = draft_issue
        self.issue = issue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Tag.expose
    def list(self):
        return DBSession.query(Tag).filter(
            Tag.organization_id == context.identity.payload['organizationId']
        )

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Tag.expose
    @commit
    def add(self, id):
        try:
            id = int(id)

        except (ValueError, TypeError):
            raise HTTPNotFound()

        tag = DBSession.query(Tag).get(id)
        if tag is None:
            raise HTTPNotFound()

        if self.draft_issue is not None:
            is_exist_tag = DBSession.query(exists().where(and_(
                DraftIssueTag.draft_issue_id == self.draft_issue.id,
                DraftIssueTag.tag_id == tag.id
            ))).scalar()
            if is_exist_tag:
                raise HTTPAlreadyTagAdded()

            draft_issue_tag = DraftIssueTag(
                tag_id=tag.id,
                draft_issue_id=self.draft_issue.id,
            )
            DBSession.add(draft_issue_tag)

        elif self.issue is not None:
            is_exist_tag = DBSession.query(exists().where(and_(
                IssueTag.issue_id == self.issue.id,
                IssueTag.tag_id == tag.id
            ))).scalar()
            if is_exist_tag:
                raise HTTPAlreadyTagAdded()

            issue_tag = IssueTag(
                tag_id=tag.id,
                issue_id=self.issue.id,
            )
            DBSession.add(issue_tag)

        else:
            raise HTTPForbidden()

        return tag

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Tag.expose
    @commit
    def remove(self, id):
        try:
            id = int(id)

        except (ValueError, TypeError):
            raise HTTPNotFound()

        tag = DBSession.query(Tag).get(id)
        if tag is None:
            raise HTTPNotFound()

        if self.draft_issue is not None:
            draft_issue_tag = DBSession.query(DraftIssueTag) \
                .filter(
                    DraftIssueTag.draft_issue_id == self.draft_issue.id,
                    DraftIssueTag.tag_id == tag.id
                ) \
                .one_or_none()
            if draft_issue_tag is None:
                raise HTTPAlreadyTagRemoved()

            else:
                DBSession.delete(draft_issue_tag)

        elif self.issue is not None:
            issue_tag = DBSession.query(IssueTag) \
                .filter(
                    IssueTag.issue_id == self.issue.id,
                    IssueTag.tag_id == tag.id
                ) \
                .one_or_none()
            if issue_tag is None:
                raise HTTPAlreadyTagRemoved()

            else:
                DBSession.delete(issue_tag)

        else:
            raise HTTPForbidden()

        return tag

