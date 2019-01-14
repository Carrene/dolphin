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

                    print(
                        f'Setting Attribute: {attribute} with value: {value}, '
                        f'Old: {getattr(self, attribute)} related to '
                        f'{type(self).__name__} with id: {self.id}'
                    )

        super().__setattr__(attribute, value)


@event.listens_for(AuditLogMixin, 'after_insert', propagate=True)
def after_insert(mapper, connection, target):
    print(f'Creating the {type(target).__name__} with id: {target.id}')

