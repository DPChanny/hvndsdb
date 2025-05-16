from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dtos.sensor_dto import (
    AddSensorRequestDTO,
    GetSensorListRequestDTO,
    GetSensorListResponseDTO,
    GetSensorDetailResponseDTO,
    UpdateSensorRequestDTO,
)
from dtos.base_dto import BaseResponseDTO
from services.sensor_service import (
    add_sensor_service,
    delete_sensor_service,
    get_sensor_list_service,
    get_sensor_detail_service,
    update_sensor_service,
)

sensor_router = APIRouter()


@sensor_router.post("/", response_model=GetSensorDetailResponseDTO)
def add_sensor_route(dto: AddSensorRequestDTO, db: Session = Depends(get_db)):
    return add_sensor_service(dto, db)


@sensor_router.get("/", response_model=GetSensorListResponseDTO)
def get_sensor_list_route(
    group_id: int = Query(None),
    crop_id: int = Query(None),
    db: Session = Depends(get_db),
):
    return get_sensor_list_service(
        GetSensorListRequestDTO(group_id=group_id, crop_id=crop_id), db
    )


@sensor_router.get("/{sensor_id}", response_model=GetSensorDetailResponseDTO)
def get_sensor_detail_route(sensor_id: int, db: Session = Depends(get_db)):
    return get_sensor_detail_service(sensor_id, db)


@sensor_router.patch("/{sensor_id}", response_model=GetSensorDetailResponseDTO)
def update_sensor_route(
    sensor_id: int, dto: UpdateSensorRequestDTO, db: Session = Depends(get_db)
):
    return update_sensor_service(sensor_id, dto, db)


@sensor_router.delete("/{sensor_id}", response_model=BaseResponseDTO[None])
def delete_sensor_route(sensor_id: int, db: Session = Depends(get_db)):
    return delete_sensor_service(sensor_id, db)
