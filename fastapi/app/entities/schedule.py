from sqlalchemy import Column, ForeignKey, Integer, Time, Enum, String
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin
import enum


class Weekday(str, enum.Enum):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"


class Schedule(Base, TimeMixin):
    __tablename__ = "schedule"

    schedule_id = Column(Integer, primary_key=True, autoincrement=True)

    crop_id = Column(
        Integer, ForeignKey("crop.crop_id", ondelete="CASCADE"), nullable=False
    )

    weekday = Column(Enum(Weekday, native_enum=False), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    author = Column(String(256), nullable=False)

    crop = relationship("Crop", back_populates="schedules")
