from datetime import time
from typing import Optional, List, Literal
from pydantic import BaseModel, field_serializer
from dtos.base_dto import BaseResponseDTO, TimeMixin
from entities.schedule import Weekday

WeekdayLiteral = Literal[*(e.value for e in Weekday)]


class ScheduleDTO(BaseModel):
    schedule_id: int
    crop_id: int

    weekday: Weekday
    start_time: time
    end_time: time
    author: str

    model_config = {"from_attributes": True}

    @field_serializer("weekday")
    def serialize_weekday(self, value: Weekday):
        return value.value


class ScheduleDetailDTO(ScheduleDTO, TimeMixin):
    pass


class AddScheduleRequestDTO(BaseModel):
    crop_id: int
    weekday: WeekdayLiteral  # type: ignore
    start_time: time
    end_time: time
    author: str


class UpdateScheduleRequestDTO(BaseModel):
    weekday: Optional[WeekdayLiteral] = None  # type: ignore
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    author: Optional[str] = None


class GetScheduleListRequestDTO(BaseModel):
    group_id: Optional[int] = None
    crop_id: Optional[int] = None


class GetScheduleListResponseDTO(BaseResponseDTO[List[ScheduleDTO]]):
    pass


class GetScheduleDetailResponseDTO(BaseResponseDTO[ScheduleDetailDTO]):
    pass
