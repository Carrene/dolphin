from auditort import context as AuditLogContext
from nanohttp import context
from restfulpy.orm import DBSession
from restfulpy.utils import to_camel_case
from sqlalchemy import event, inspect


class AuditLogMixin:

    def __setattr__(self, attribute, value):

        if attribute != '_sa_instance_state':
            mapper_info = inspect(self)

            if not mapper_info.pending and \
                self in DBSession and \
                to_camel_case(attribute) in self.json_metadata()['fields'] and \
                value != getattr(self, attribute):

                    AuditLogContext.append_change_attribute(
                        user=context.identity.email,
                        obj=self,
                        attribute=attribute,
                        old_value=getattr(self, attribute),
                        new_value=value,
                    )

        super().__setattr__(attribute, value)


@event.listens_for(AuditLogMixin, 'after_insert', propagate=True)
def after_insert(mapper, connection, target):
    try:
        email = context.identity.email

    except:
        email = 'anonymous'

    AuditLogContext.append_instantiation(user=email, obj=target)

