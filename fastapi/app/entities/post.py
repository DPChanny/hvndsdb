from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin


class Post(Base, TimeMixin):
    __tablename__ = "post"

    post_id = Column(Integer, primary_key=True, autoincrement=True)
    crop_id = Column(
        Integer, ForeignKey("crop.crop_id", ondelete="CASCADE"), nullable=False
    )

    content = Column(Text, nullable=False)
    image_url = Column(String(256), nullable=True)
    author = Column(String(256), nullable=False)

    crop = relationship("Crop", back_populates="posts")

    comments = relationship(
        "Comment", back_populates="post", passive_deletes=True
    )
