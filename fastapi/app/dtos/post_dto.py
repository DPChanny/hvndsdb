from typing import Optional, List
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin
from dtos.comment_dto import CommentDetailDTO


class PostDTO(BaseModel):
    post_id: int
    crop_id: int

    content: str
    image_url: str
    author: str

    model_config = {"from_attributes": True}


class PostDetailDTO(PostDTO, TimeMixin):
    comments: List[CommentDetailDTO]


class AddPostRequestDTO(BaseModel):
    crop_id: int
    content: str
    author: str


class UpdatePostRequestDTO(BaseModel):
    content: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None


class GetPostListRequestDTO(BaseModel):
    group_id: Optional[int] = None
    crop_id: Optional[int] = None


class GetPostListResponseDTO(BaseResponseDTO[List[PostDTO]]):
    pass


class GetPostDetailResponseDTO(BaseResponseDTO[PostDetailDTO]):
    pass
