from nanohttp import json, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Member, Manager
from .managers import ManagerController


class MemberController(ModelRestController):
    __model__ = Member
    _manager_controller = ManagerController()

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1 and remaining_paths[1] == 'managers':
            return self._manager_controller(remaining_paths[0])

