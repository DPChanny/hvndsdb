from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dtos.user_dto import (
    AddUserRequestDTO,
    UpdateUserRequestDTO,
    GetUserDetailResponseDTO,
    GetUserListRequestDTO,
    GetUserListResponseDTO,
)
from dtos.base_dto import BaseResponseDTO
from services.user_service import (
    add_user_service,
    get_user_list_service,
    update_user_service,
    delete_user_service,
    get_user_detail_service,
)
from uuid import UUID

user_router = APIRouter()

@user_router.post("/", response_model=GetUserDetailResponseDTO)
def add_user_route(dto: AddUserRequestDTO, db: Session = Depends(get_db)):
    return add_user_service(dto, db)

@user_router.get("/", response_model=GetUserListResponseDTO)
def get_user_list_route(query: str = Query(None), db: Session = Depends(get_db)):
    return get_user_list_service(GetUserListRequestDTO(query=query), db)

@user_router.get("/{user_id}", response_model=GetUserDetailResponseDTO)
def get_user_detail_route(user_id: UUID, db: Session = Depends(get_db)):
    return get_user_detail_service(user_id, db)

@user_router.patch("/{user_id}", response_model=GetUserDetailResponseDTO)
def update_user_route(user_id: UUID, dto: UpdateUserRequestDTO, db: Session = Depends(get_db)):
    return update_user_service(user_id, dto, db)

@user_router.delete("/{user_id}", response_model=BaseResponseDTO[None])
def delete_user_route(user_id: UUID, db: Session = Depends(get_db)):
    return delete_user_service(user_id, db) 