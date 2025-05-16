from typing import Literal, Optional, List
from pydantic import BaseModel, field_serializer
from dtos.base_dto import BaseResponseDTO, TimeMixin
from entities.sensor import SensorType

SensorTypeLiteral = Literal[*(e.value for e in SensorType)]


class SensorDTO(BaseModel):
    sensor_id: int
    crop_id: int

    value: str
    name: str
    sensor_type: SensorType

    model_config = {"from_attributes": True}

    @field_serializer("sensor_type")
    def serialize_sensor_type(self, value: SensorType):
        return value.value


class SensorDetailDTO(SensorDTO, TimeMixin):
    pass


class AddSensorRequestDTO(BaseModel):
    crop_id: int
    name: str
    sensor_type: SensorTypeLiteral  # type: ignore


class UpdateSensorRequestDTO(BaseModel):
    name: Optional[str] = None
    sensor_type: Optional[SensorTypeLiteral] = None  # type: ignore
    value: Optional[str] = None


class GetSensorListRequestDTO(BaseModel):
    group_id: Optional[int] = None
    crop_id: Optional[int] = None


class GetSensorListResponseDTO(BaseResponseDTO[List[SensorDTO]]):
    pass


class GetSensorDetailResponseDTO(BaseResponseDTO[SensorDetailDTO]):
    pass
