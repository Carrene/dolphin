from easycli import SubCommand, Argument


class MuleSubSubCommand(SubCommand):  # pragma: no cover
    __help__ = 'Background worker start.'
    __command__ = 'start'

    def __call__(self, args):
        print('Hello')


class MuleSubCommand(SubCommand): # pragma: no cover
    __help__ = 'Background worker.'
    __command__ = 'mule'
    __arguments__ = [
        MuleSubSubCommand,
    ]

