from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import Group, GroupMember, Member
from ..validators import group_create_validator, group_add_validator, \
    group_remove_validator, group_update_validator
from ..exceptions import StatusMemberNotFound, StatusAlreadyAddedToGroup, \
    StatusMemberNotExistsInGroup, StatusRepetitiveTitle


FORM_WHITELIST = [
    'title',
    'description',
    'public',
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class GroupController(ModelRestController):
    __model__ = Group

    @authorize
    @json
    @Group.expose
    def list(self):
        return DBSession.query(Group)

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Group.expose
    def get(self, id):
        id = int_or_notfound(id)
        group = DBSession.query(Group).get(id)

        if not group:
            raise HTTPNotFound()

        return group

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @group_create_validator
    @commit
    def create(self):
        group = Group(
            title=context.form.get('title'),
            description=context.form.get('description'),
        )
        DBSession.add(group)
        return group

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @group_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        title = context.form.get('title')
        group = DBSession.query(Group).get(id)
        if group is None:
            raise HTTPNotFound()

        is_exist_group = DBSession.query(Group) \
            .filter(Group.title == title) \
            .one_or_none()
        if group.title != title and is_exist_group is not None:
            raise StatusRepetitiveTitle()

        group.update_from_request()
        return group

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @group_add_validator
    @commit
    def add(self, id):
        id = int_or_notfound(id)
        group = DBSession.query(Group).get(id)
        if group is None:
            raise HTTPNotFound()

        member = DBSession.query(Member).get(context.form.get('memberId'))
        if member is None:
            raise StatusMemberNotFound()

        group_member = DBSession.query(GroupMember) \
            .filter(
                GroupMember.group_id == id,
                GroupMember.member_id == member.id
            ) \
            .one_or_none()
        if group_member is not None:
            raise StatusAlreadyAddedToGroup()

        group.members.append(member)
        return group

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @group_remove_validator
    @commit
    def remove(self, id):
        id = int_or_notfound(id)
        group = DBSession.query(Group).get(id)
        if group is None:
            raise HTTPNotFound()

        member = DBSession.query(Member).get(context.form.get('memberId'))
        if member is None:
            raise StatusMemberNotFound()

        group_member = DBSession.query(GroupMember) \
            .filter(
                GroupMember.group_id == id,
                GroupMember.member_id == member.id
            ) \
            .one_or_none()
        if group_member is None:
            raise StatusMemberNotExistsInGroup()

        group.members.remove(member)
        return group

