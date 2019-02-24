from nanohttp import json, context, HTTPNotFound, HTTPUnauthorized, \
    int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController, JsonPatchControllerMixin
from restfulpy.orm import commit, DBSession

from ..backends import ChatClient
from ..exceptions import RoomMemberAlreadyExist, ChatRoomNotFound
from ..models import Issue, Phase, Item, Member, DraftIssue, DraftIssueTag, \
    Tag, Skill, Resource
from ..validators import draft_issue_finalize_validator
from .tag import TagController


FORM_WHITELIST = [
    'title',
    'description',
    'kind',
    'days',
    'status',
    'projectId',
    'dueDate',
    'priority'
]


FROM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class DraftIssueController(ModelRestController, JsonPatchControllerMixin):
    __model__ = DraftIssue

    def _ensure_room(self, title, token, access_token):
        create_room_error = 1
        room = None
        while create_room_error is not None:
            try:
                room = ChatClient().create_room(
                    title,
                    token,
                    access_token,
                    context.identity.reference_id
                )
                create_room_error = None

            except ChatRoomNotFound:
                create_room_error = 1

        return room

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1:

            if not context.identity:
                raise HTTPUnauthorized()

            id = int_or_notfound(remaining_paths[0])

            draft_issue = DBSession.query(DraftIssue).get(id)
            if draft_issue is None:
                raise HTTPNotFound()

            if remaining_paths[1] == 'tags':
                return TagController(draft_issue=draft_issue) \
                    (*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    @authorize
    @json(form_whitelist=(
        FORM_WHITELIST,
        f'707 Invalid field, only following fields are accepted: '
        f'{FROM_WHITELISTS_STRING}'
    ))
    @DraftIssue.expose
    @commit
    def define(self):
        draft_issue = DraftIssue()
        DBSession.add(draft_issue)
        return draft_issue

    @authorize
    @json(form_whitelist=(
        FORM_WHITELIST,
        f'707 Invalid field, only following fields are accepted: '
        f'{FROM_WHITELISTS_STRING}'
    ))
    @draft_issue_finalize_validator
    @DraftIssue.expose
    @commit
    def finalize(self, id):
        id = int_or_notfound(id)

        draft_issue = DBSession.query(DraftIssue).get(id)
        if draft_issue is None:
            raise HTTPNotFound()

        tags = DBSession.query(Tag) \
            .join(DraftIssueTag, DraftIssueTag.tag_id == Tag.id) \
            .filter(DraftIssueTag.draft_issue_id == id) \
            .all()

        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        issue = Issue()
        issue.tags = tags
        issue.update_from_request()

        current_member = Member.current()
        room = self._ensure_room(
            form['title'],
            token,
            current_member.access_token
        )

        chat_client = ChatClient()
        issue.room_id = room['id']
        try:
            chat_client.add_member(
                issue.room_id,
                current_member.reference_id,
                token,
                current_member.access_token
            )

        except RoomMemberAlreadyExist:
            # Exception is passed because it means `add_member()` is already
            # called and `member` successfully added to room. So there is
            # no need to call `add_member()` API again and re-add the member to
            # room.
            pass

        # The exception type is not specified because after consulting with
        # Mr.Mardani, the result got: there must be no specification on
        # exception type because nobody knows what exception may be raised
        try:
            issue.room_id = room['id']

        except:
            chat_client.delete_room(
                issue.room_id,
                token,
                current_member.access_token
            )
            raise

        DBSession.add(issue)
        DBSession.flush()
        draft_issue.issue_id = issue.id
        return draft_issue

