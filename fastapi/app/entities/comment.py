from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin


class Comment(Base, TimeMixin):
    __tablename__ = "comment"

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(
        Integer, ForeignKey("post.post_id", ondelete="CASCADE"), nullable=False
    )

    author = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)

    post = relationship("Post", back_populates="comments")
