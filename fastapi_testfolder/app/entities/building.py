from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin
import uuid

class Building(Base, TimeMixin):
    __tablename__ = "building"

    building_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256), nullable=False)
    address = Column(String(256), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    is_ready = Column(Boolean, default=False)
    s3_url = Column(String(512), nullable=True)

    user = relationship("User", back_populates="buildings")

    
