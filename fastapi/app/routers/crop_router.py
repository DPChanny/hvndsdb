from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dtos.crop_dto import (
    AddCropRequestDTO,
    GetCropDetailResponseDTO,
    GetCropListRequestDTO,
    GetCropListResponseDTO,
    UpdateCropRequestDTO,
)
from dtos.base_dto import BaseResponseDTO
from services.crop_service import (
    add_crop_service,
    delete_crop_service,
    get_crop_list_service,
    get_crop_detail_service,
    update_crop_service,
)

crop_router = APIRouter()


@crop_router.post("/", response_model=GetCropDetailResponseDTO)
def add_crop_route(dto: AddCropRequestDTO, db: Session = Depends(get_db)):
    return add_crop_service(dto, db)


@crop_router.get("/", response_model=GetCropListResponseDTO)
def get_crop_list_route(
    group_id: int = Query(None),
    db: Session = Depends(get_db),
):
    return get_crop_list_service(GetCropListRequestDTO(group_id=group_id), db)


@crop_router.get("/{crop_id}", response_model=GetCropDetailResponseDTO)
def get_crop_detail_route(crop_id: int, db: Session = Depends(get_db)):
    return get_crop_detail_service(crop_id, db)


@crop_router.patch("/{crop_id}", response_model=GetCropDetailResponseDTO)
def update_crop_route(
    crop_id: int, dto: UpdateCropRequestDTO, db: Session = Depends(get_db)
):
    return update_crop_service(crop_id, dto, db)


@crop_router.delete("/{crop_id}", response_model=BaseResponseDTO[None])
def delete_crop_route(crop_id: int, db: Session = Depends(get_db)):
    return delete_crop_service(crop_id, db)
