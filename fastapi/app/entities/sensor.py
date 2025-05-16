from sqlalchemy import Column, ForeignKey, String, Integer, Enum
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin
import enum


class SensorType(str, enum.Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"
    WATER = "water"


class Sensor(Base, TimeMixin):
    __tablename__ = "sensor"

    sensor_id = Column(Integer, primary_key=True, autoincrement=True)

    crop_id = Column(
        Integer, ForeignKey("crop.crop_id", ondelete="CASCADE"), nullable=False
    )

    name = Column(String(256), nullable=False)
    value = Column(String(256), default="NaN", nullable=False)
    sensor_type = Column(Enum(SensorType, native_enum=False), nullable=False)

    crop = relationship("Crop", back_populates="sensors")
