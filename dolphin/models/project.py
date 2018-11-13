from restfulpy.orm import Field, DeclarativeBase


class Project(DeclarativeBase):

    __tablename__ = 'project'

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
        not_none=False,
        required=True,
        python_type=str
    )

