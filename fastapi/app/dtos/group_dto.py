from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin
from dtos.crop_dto import CropDetailDTO


class GroupDTO(BaseModel):
    group_id: int

    name: str
    location: str

    model_config = {"from_attributes": True}


class GroupDetailDTO(GroupDTO, TimeMixin):
    crops: list[CropDetailDTO]


class AddGroupRequestDTO(BaseModel):
    name: str
    location: str


class GetGroupListRequestDTO(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class UpdateGroupRequestDTO(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class GetGroupListResponseDTO(BaseResponseDTO[List[GroupDTO]]):
    pass


class GetGroupDetailResponseDTO(BaseResponseDTO[GroupDetailDTO]):
    pass
