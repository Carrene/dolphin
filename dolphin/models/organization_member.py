from restfulpy.orm import Field, PaginationMixin, FilteringMixin, \
    OrderingMixin, BaseModel, MetadataField
from sqlalchemy import Integer, Unicode, select
from sqlalchemy.orm import mapper

from . import OrganizationMember, Member


class AbstractOrganizationMemberView(PaginationMixin, OrderingMixin,
                                     FilteringMixin, BaseModel):
    __abstract__ = True
    __table_args__ = {'autoload': True}

    id = Field(Integer, primary_key=True)
    email = Field(Unicode(100))
    title = Field(Unicode(100))
    name = Field(Unicode(20))
    phone = Field(Unicode(16))
    avatar = Field(Unicode)
    access_token = Field(Unicode(512))
    organization_role = Field(Unicode)
    organization_id = Field(Integer)

    @classmethod
    def create_mapped_class(cls):
        query = select([
            Member,
            OrganizationMember.role.label('organization_role'),
            OrganizationMember.organization_id,
        ]).select_from(Member.__table__.join(
            OrganizationMember,
            OrganizationMember.member_id == Member.id
        )).cte()

        class OrganizationMemberView(cls):
            pass

        mapper(OrganizationMemberView, query.alias())
        return OrganizationMemberView

    def to_dict(self):
        organization_member = super().to_dict()
        organization_member['organizationRole'] = self.organization_role
        return organization_member

    @classmethod
    def iter_columns(cls, relationships=True, synonyms=True, composites=True,
                     use_inspection=False, hybrids=True):
         for c in Member.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
            use_inspection=use_inspection
        ):
            column = getattr(cls, c.key, None)
            if hasattr(c, 'info'):
                column.info.update(c.info)
            yield column

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='organizationRole',
            key='organization_role',
            label='Organization Role',
            example='lorem ipsum',
            readonly=True,
            watermark='lorem ipsum',
            type_=str,
            required=True,
            not_none=True,
        )

