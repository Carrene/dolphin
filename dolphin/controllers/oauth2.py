from restfulpy.controllers import RestController

from .member import MemberController


class OAUTHController(RestController):
    _member_controller = MemberController()

    def __call__(self, *remaining_paths):
        if len(remaining_paths) == 1 and remaining_paths[0] == 'members':
            return self._member_controller()

