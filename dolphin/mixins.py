from datetime import datetime

from nanohttp import context
from sqlalchemy import Integer
from sqlalchemy.events import event
from restfulpy.orm import ModifiedMixin, Field


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

