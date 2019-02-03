from nanohttp import json, HTTPNotFound, context, HTTPStatus, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy_media import store_manager

from ..models import Attachment, Member
from ..validators import attachment_validator


class FileController(ModelRestController):
    __model__ = Attachment

    def __init__(self, project=None, issue=None):
        self.project = project
        self.issue = issue

    @authorize
    @store_manager(DBSession)
    @json
    @attachment_validator
    @commit
    def attach(self):
        form=context.form

        if not (self.project or self.issue):
            raise HTTPNotFound()

        current_member = DBSession.query(Member) \
            .filter(Member.reference_id == context.identity.reference_id) \
            .one()
        attachment = Attachment(
            file=form['attachment'],
            caption=form['caption'] if 'caption' in form else None,
            sender_id=current_member.id
        )
        attachment.title = form['title'] \
            if 'title' in form else attachment.file.original_filename

        if self.project:
            attachment.project_id = self.project.id

        elif self.issue:
            attachment.issue_id = self.issue.id

        DBSession.add(attachment)
        return attachment

    @authorize
    @store_manager(DBSession)
    @json
    @Attachment.expose
    @commit
    def delete(self, id):
        id = int_or_notfound(id)

        attachment = DBSession.query(Attachment).get(id)
        if attachment is None:
            raise HTTPNotFound()

        if attachment.is_deleted:
            raise HTTPStatus('629 Attachment Already Deleted')

        attachment.soft_delete()
        return attachment

    @authorize
    @store_manager(DBSession)
    @json
    @Attachment.expose
    @commit
    def list(self):
        query = DBSession.query(Attachment) \
            .filter(Attachment.project_id == self.project.id)

        return Attachment.exclude_deleted(query)

