from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dtos.schedule_dto import (
    AddScheduleRequestDTO,
    GetScheduleListRequestDTO,
    GetScheduleListResponseDTO,
    GetScheduleDetailResponseDTO,
    UpdateScheduleRequestDTO,
)
from dtos.base_dto import BaseResponseDTO
from services.schedule_service import (
    add_schedule_service,
    delete_schedule_service,
    get_schedule_list_service,
    get_schedule_detail_service,
    update_schedule_service,
)

schedule_router = APIRouter()


@schedule_router.post("/", response_model=GetScheduleDetailResponseDTO)
def add_schedule_route(
    dto: AddScheduleRequestDTO, db: Session = Depends(get_db)
):
    return add_schedule_service(dto, db)


@schedule_router.get("/", response_model=GetScheduleListResponseDTO)
def get_schedule_list_route(
    group_id: int = Query(None),
    crop_id: int = Query(None),
    db: Session = Depends(get_db),
):
    return get_schedule_list_service(
        GetScheduleListRequestDTO(group_id=group_id, crop_id=crop_id), db
    )


@schedule_router.get(
    "/{schedule_id}", response_model=GetScheduleDetailResponseDTO
)
def get_schedule_detail_route(schedule_id: int, db: Session = Depends(get_db)):
    return get_schedule_detail_service(schedule_id, db)


@schedule_router.patch(
    "/{schedule_id}", response_model=GetScheduleDetailResponseDTO
)
def update_schedule_route(
    schedule_id: int,
    dto: UpdateScheduleRequestDTO,
    db: Session = Depends(get_db),
):
    return update_schedule_service(schedule_id, dto, db)


@schedule_router.delete("/{schedule_id}", response_model=BaseResponseDTO[None])
def delete_schedule_route(schedule_id: int, db: Session = Depends(get_db)):
    return delete_schedule_service(schedule_id, db)
