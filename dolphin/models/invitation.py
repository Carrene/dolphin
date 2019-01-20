from datetime  import datetime

from restfulpy.orm import DeclarativeBase, Field, relationship, \
    ModifiedMixin, TimestampMixin, FilteringMixin, OrderingMixin, \
    PaginationMixin
from sqlalchemy import Unicode, Integer, ForeignKey, Enum, Boolean, DateTime, \
    case
from sqlalchemy.ext.hybrid import hybrid_property


roles = [
    'owner',
    'member',
]


class Invitation(OrderingMixin, FilteringMixin, PaginationMixin,
                 ModifiedMixin, TimestampMixin, DeclarativeBase):

    __tablename__ = 'invitation'

    id = Field(Integer, primary_key=True, readonly=True)

    organization_id = Field(
        Integer,
        ForeignKey('organization.id'),
        python_type=int,
        watermark='Choose a organization',
        label='Organization',
        readonly=True,
        not_none=True,
        required=False,
        example='Lorem Ipsum'
    )
    by_member_id = Field(
        Integer,
        ForeignKey('member.id'),
        python_type=int,
        watermark='Choose a member',
        label='Member',
        readonly=True,
        not_none=True,
        required=False,
        example='Lorem Ipsum'
    )
    role = Field(
        Enum(*roles, name='roles'),
        python_type=str,
        label='role',
        watermark='Choose a role',
        not_none=True,
        required=True,
        example='Lorem Ipsum'
    )
    accepted = Field(Boolean, default=False, readonly=True)
    expired_date = Field(
        DateTime,
        python_type=datetime,
        label='Expired Date',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        watermark='lorem ipsum',
        readonly=True,
        nullable=False,
        not_none=True,
        required=True,
    )
    email = Field(
        Unicode(100),
        unique=True,
        not_none=False,
        required=True,
        index=True,
        python_type=str,
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
        pattern_description='Invalid email format, example: user@example.com',
        watermark='lorem ipsum',
        example='lorem ipsum',
        label='Invited Email'
    )

    by_member = relationship(
        'Member',
        back_populates='invitations',
        protected=True
    )
    organization = relationship(
        'Organization',
        back_populates='invitations',
        protected=True
    )

    @hybrid_property
    def status(self):
        if self.expired_date < datetime.now():
            return 'expired'
        elif self.expired_date > datetime.now():
            return 'pending'
        else:
            return 'accepted'

    @status.expression
    def status(cls):
        return case([
            (cls.accepted, 'accepted'),
            (cls.expired_date < datetime.now(), 'expired'),
            (cls.expired_date > datetime.now(), 'pending')
        ])

