from typing import Literal, Optional, List
from pydantic import BaseModel, field_serializer
from dtos.base_dto import BaseResponseDTO, TimeMixin
from dtos.schedule_dto import ScheduleDTO
from dtos.sensor_dto import SensorDTO
from dtos.post_dto import PostDTO
from entities.crop import CropType

CropTypeLiteral = Literal[*(e.value for e in CropType)]


class CropDTO(BaseModel):
    crop_id: int
    group_id: int

    name: str
    crop_type: CropType
    harvest: bool

    model_config = {"from_attributes": True}

    @field_serializer("crop_type")
    def serialize_crop_type(self, value: CropType):
        return value.value


class CropDetailDTO(CropDTO, TimeMixin):
    posts: List[PostDTO]
    schedules: List[ScheduleDTO]
    sensors: List[SensorDTO]


class AddCropRequestDTO(BaseModel):
    group_id: int
    name: str
    crop_type: CropTypeLiteral  # type: ignore


class GetCropListRequestDTO(BaseModel):
    group_id: Optional[int] = None


class UpdateCropRequestDTO(BaseModel):
    name: Optional[str] = None
    crop_type: Optional[CropTypeLiteral] = None  # type: ignore
    harvest: Optional[bool] = None


class GetCropListResponseDTO(BaseResponseDTO[List[CropDTO]]):
    pass


class GetCropDetailResponseDTO(BaseResponseDTO[CropDetailDTO]):
    pass
