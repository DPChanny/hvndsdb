import enum
from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, Enum
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin


class CropType(str, enum.Enum):
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    GRAIN = "grain"
    HERB = "herb"
    FLOWER = "flower"


class Crop(Base, TimeMixin):
    __tablename__ = "crop"

    crop_id = Column(Integer, primary_key=True, autoincrement=True)

    group_id = Column(
        Integer,
        ForeignKey("group.group_id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String(256), nullable=False)
    crop_type = Column(Enum(CropType, native_enum=False), nullable=False)
    harvest = Column(Boolean, default=False, nullable=False)

    group = relationship("Group", back_populates="crops")

    posts = relationship("Post", back_populates="crop", passive_deletes=True)
    schedules = relationship(
        "Schedule", back_populates="crop", passive_deletes=True
    )
    sensors = relationship(
        "Sensor", back_populates="crop", passive_deletes=True
    )
