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

    @property
    def last_modifier_member(self):
        return self.modified_by

    @classmethod
    def before_update(cls, mapper, connection, target):
        super().before_update(mapper, connection, target)
        if not target.object.__exclude__.issubset(target.unmodified):
            return

        target.object.modified_by = context.identity.reference_id

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls.before_update, raw=True)

