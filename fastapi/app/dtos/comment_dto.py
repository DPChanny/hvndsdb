from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin


class CommentDTO(BaseModel):
    comment_id: int
    post_id: int

    content: str
    author: str

    model_config = {"from_attributes": True}


class CommentDetailDTO(CommentDTO, TimeMixin):
    pass


class AddCommentRequestDTO(BaseModel):
    post_id: int
    content: str
    author: str


class UpdateCommentRequestDTO(BaseModel):
    content: str


class GetCommentListRequestDTO(BaseModel):
    post_id: Optional[int] = None


class GetCommentListResponseDTO(BaseResponseDTO[List[CommentDTO]]):
    pass


class GetCommentDetailResponseDTO(BaseResponseDTO[CommentDetailDTO]):
    pass
