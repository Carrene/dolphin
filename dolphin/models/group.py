from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, String, ForeignKey


class GroupMember(DeclarativeBase):
    __tablename__ = 'group_member'

    group_id = Field(Integer, ForeignKey('group.id'), primary_key=True)
    member_id = Field(Integer, ForeignKey('member.id'), primary_key=True)


class Group(DeclarativeBase):
    __tablename__ = 'group'

    id = Field(Integer, primary_key=True)
    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Name',
        watermark='Enter the name',
        pattern=r'^[^\s].+[^\s]$',
        example='Sample Title',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )

    projects = relationship(
        'Project',
        back_populates='group',
        protected=True
    )
    members = relationship(
        'Member',
        back_populates='groups',
        secondary='group_member',
        protected=True
    )

