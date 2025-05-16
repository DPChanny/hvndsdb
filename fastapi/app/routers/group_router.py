from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dtos.group_dto import (
    AddGroupRequestDTO,
    GetGroupDetailResponseDTO,
    GetGroupListResponseDTO,
    GetGroupListRequestDTO,
    UpdateGroupRequestDTO,
)
from dtos.base_dto import BaseResponseDTO
from services.group_service import (
    add_group_service,
    delete_group_service,
    get_group_list_service,
    get_group_detail_service,
    update_group_service,
)

group_router = APIRouter()


@group_router.post("/", response_model=GetGroupDetailResponseDTO)
def add_group_route(dto: AddGroupRequestDTO, db: Session = Depends(get_db)):
    return add_group_service(dto, db)


@group_router.get("/", response_model=GetGroupListResponseDTO)
def get_group_list_route(
    name: str = Query(None),
    location: str = Query(None),
    db: Session = Depends(get_db),
):
    return get_group_list_service(
        GetGroupListRequestDTO(name=name, location=location), db
    )


@group_router.get("/{group_id}", response_model=GetGroupDetailResponseDTO)
def get_group_detail_route(group_id: int, db: Session = Depends(get_db)):
    return get_group_detail_service(group_id, db)


@group_router.patch("/{group_id}", response_model=GetGroupDetailResponseDTO)
def update_group_route(
    group_id: int, dto: UpdateGroupRequestDTO, db: Session = Depends(get_db)
):
    return update_group_service(group_id, dto, db)


@group_router.delete("/{group_id}", response_model=BaseResponseDTO[None])
def delete_group_route(group_id: int, db: Session = Depends(get_db)):
    return delete_group_service(group_id, db)
