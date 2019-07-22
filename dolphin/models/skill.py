from auditor import observe
from nanohttp import context
from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam, \
    join, case, exists
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property

from ..mixins import ModifiedByMixin
from .issue import Issue, Boarding
from .member import Member
from .subscribable import Subscribable, Subscription


class Skill(Subscribable):
    __tabelname__ = 'skill'
    __mapper_args__ = {'polymorphic_identity': __tabelname__}

    id = Field(
        Integer,
        ForeignKey('subscribable.id'),
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
    title = Field(
        String(50),
        max_length=50,
        min_length=1,
        label='Name',
        watermark='Enter the name',
        example='Sample Title',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )
    description = Field(
        String(512),
        max_length=512,
        label='Description',
        watermark='Lorem Ipusm',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum'
    )
    specialties = relationship(
        'Specialty',
        back_populates='skill',
        protected=True
    )

