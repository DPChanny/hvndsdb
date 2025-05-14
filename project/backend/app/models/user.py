from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

# ORM 모델
class UserORM(Base):
    __tablename__ = 'user'
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

class BuildingORM(Base):
    __tablename__ = 'building'
    building_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'))
    is_ready = Column(Boolean, default=False)
    s3_url = Column(String)

# Pydantic 모델
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    user_id: uuid.UUID
    class Config:
        orm_mode = True

class BuildingBase(BaseModel):
    name: str
    address: str
    is_ready: bool = False
    s3_url: str = None

class BuildingCreate(BuildingBase):
    user_id: uuid.UUID

class BuildingRead(BuildingBase):
    building_id: uuid.UUID
    user_id: uuid.UUID
    class Config:
        orm_mode = True
