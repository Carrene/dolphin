from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import Group, GroupMember, Member
from ..validators import group_create_validator, group_add_validator, \
    group_remove_validator
from ..exceptions import HTTPMemberNotFound, HTTPAlreadyAddedToGroup, \
    HTTPMemberNotExistsInGroup


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
            title=context.form.get('title')
        )
        DBSession.add(group)
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
            raise HTTPMemberNotFound()

        group_member = DBSession.query(GroupMember) \
            .filter(
                GroupMember.group_id == id,
                GroupMember.member_id == member.id
            ) \
            .one_or_none()
        if group_member is not None:
            raise HTTPAlreadyAddedToGroup()

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
            raise HTTPMemberNotFound()

        group_member = DBSession.query(GroupMember) \
            .filter(
                GroupMember.group_id == id,
                GroupMember.member_id == member.id
            ) \
            .one_or_none()
        if group_member is None:
            raise HTTPMemberNotExistsInGroup()

        group.members.remove(member)
        return group

