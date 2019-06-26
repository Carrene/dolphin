from nanohttp import context
from restfulpy.orm import ModifiedMixin, Field
from sqlalchemy import Integer
from sqlalchemy.events import event

from .models import Member


class ModifiedByMixin(ModifiedMixin):
    modified_by = Field(
        Integer,
        nullable=True,
        name='modifiedBy',
        key='modified_by',
        readonly=True,
        label='Modified By'
    )

    @staticmethod
    def before_update(mapper, connection, target):
        super(ModifiedByMixin, ModifiedByMixin).before_update(
            mapper,
            connection,
            target
        )
        target.object.modified_by = context.identity.reference_id

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls.before_update, raw=True)


class CreatedByMixin:
    created_by_reference_id = Field(
        Integer,
        json='createdByReferenceId',
        nullable=False,
        readonly=True,
        not_none=True,
        required=False,
        protected=False,
        default=lambda: context.identity.reference_id,
        label='Created By',
        example='Lorem Ipsum',
        message='Lorem Ipsum',
        watermark='Lorem Ipsum',
    )

    created_by_member_id = Field(
        Integer,
        json='createdByMemberId',
        nullable=False,
        readonly=True,
        not_none=True,
        required=False,
        protected=False,
        default=lambda: Member.current().id,
        label='Created By',
        example='Lorem Ipsum',
        message='Lorem Ipsum',
        watermark='Lorem Ipsum',
    )

