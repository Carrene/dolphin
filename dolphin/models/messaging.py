from nanohttp import settings
from restfulpy.messaging import Email
from restfulpy.orm import Field
from restfulpy.taskqueue import RestfulpyTask
from restfulpy.utils import construct_class_by_name
from sqlalchemy import Integer, ForeignKey, Unicode, BigInteger
from sqlalchemy.orm import synonym


class RegisterEmail(Email):
    __mapper_args__ = {
        'polymorphic_identity': 'register_email'
    }

    template_filename = 'register_email.mako'


class ResetPasswordEmail(Email):
    __mapper_args__ = {
        'polymorphic_identity': 'reset_password_email'
    }

    template_filename = 'reset_password_email.mako'


class OrganizationInvitationEmail(Email):
    __mapper_args__ = {
        'polymorphic_identity': 'organization_invitation_email'
    }

    template_filename = 'organization_invitation_email.mako'


class SMS(RestfulpyTask):  # pragma: no cover
    __tablename__ = 'sms'
    _provider = None

    body = Field(Unicode(140), json='body')
    receiver = Field(BigInteger, json='receiver')

    __mapper_args__ = {
        'polymorphic_identity': __tablename__
    }

    id = Field(
        Integer,
        ForeignKey('restfulpy_task.id'),
        primary_key=True,
        json='id'
    )

    @classmethod
    def get_provider(cls):
        if cls._provider is None:
            cls._provider = create_sms_provider()
        return cls._provider

    def send(self, receiver, text):
        provider = self.get_provider()
        provider.send(receiver, text)

    def do_(self, context):
        self.send(self.receiver, self.body)


class OTPSMS(SMS):  # pragma: no cover

    _code = Field(Unicode, nullable=True, protected=True)

    def _set_code(self, code):
        self._code = code
        self.body = f'Your validation code is: {code}, please enter this ' \
                    f'code into application to validate.'

    def _get_code(self):
        return self._code

    code = synonym(
        '_code',
        descriptor=property(_get_code, _set_code),
        info=dict(protected=True)
    )

    __mapper_args__ = {
        'polymorphic_identity': 'otpsms',
    }


def create_sms_provider():  # pragma: no cover
    return construct_class_by_name(settings.sms.provider)

