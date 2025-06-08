from sqlalchemy import Column, Double, String
from utils.database import Base
from entities.time_mixin import TimeMixin
import uuid


class Building(Base, TimeMixin):
    __tablename__ = "building"

    building_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = Column(String(256), nullable=False)
    longitude = Column(Double, nullable=False)
    latitude = Column(Double, nullable=False)
