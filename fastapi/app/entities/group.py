from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin


class Group(Base, TimeMixin):
    __tablename__ = "group"

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    location = Column(String(256), nullable=False)

    crops = relationship("Crop", back_populates="group", passive_deletes=True)
