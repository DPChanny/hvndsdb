from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin


class BuildingDTO(BaseModel):
    building_id: str
    name: str
    longitude: float
    latitude: float

    model_config = {"from_attributes": True}


class BuildingDetailDTO(BuildingDTO, TimeMixin):
    analyzing: bool
    sample: bool
    frames: bool
    colmap: bool
    deblur_gs: bool
    ply: bool


class AddBuildingRequestDTO(BaseModel):
    name: str
    longitude: float
    latitude: float


class UpdateBuildingRequestDTO(BaseModel):
    name: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None


class GetBuildingDetailResponseDTO(BaseResponseDTO[BuildingDetailDTO]):
    pass


class GetBuildingListRequestDTO(BaseModel):
    query: Optional[str] = None


class GetBuildingListResponseDTO(BaseResponseDTO[List[BuildingDTO]]):
    pass
