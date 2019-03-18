from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, String, BOOLEAN, ForeignKey


class GroupMember(DeclarativeBase):
    __tablename__ = 'group_member'

    group_id = Field(Integer, ForeignKey('group.id'), primary_key=True)
    member_id= Field(Integer, ForeignKey('member.id'), primary_key=True)


class Group(DeclarativeBase):
    __tablename__ = 'group'

    id = Field(
        Integer,
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
        String,
        max_length=50,
        label='Title',
        not_none=False,
        required=True,
        unique=True,
        readonly=True,
        watermark='lorem ipsum',
        message='lorem ipsum',
        example='lorem ipsum',
    )
    public = Field(
        BOOLEAN,
        unique=True,
        nullable=True,
        required=False,
        not_none=False,
        label='Public',
    )

    projects = relationship('Project', back_populates='group', protected=True)

    members = relationship(
        'Member',
        secondary='group_member',
        lazy='selectin',
        back_populates='groups',
        protected=True,
    )

    def __repr__(self):
        return f'\tTitle: {self.title}, Public: {self.public}'

