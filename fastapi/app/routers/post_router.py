from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db

from dtos.base_dto import BaseResponseDTO
from dtos.post_dto import (
    AddPostRequestDTO,
    UpdatePostRequestDTO,
    GetPostListRequestDTO,
    GetPostListResponseDTO,
    GetPostDetailResponseDTO,
)

from services.post_service import (
    add_post_service,
    get_post_detail_service,
    get_post_list_service,
    update_post_service,
    delete_post_service,
)

post_router = APIRouter()


@post_router.post("/", response_model=GetPostDetailResponseDTO)
def add_post_route(dto: AddPostRequestDTO, db: Session = Depends(get_db)):
    return add_post_service(dto, db)


@post_router.get("/", response_model=GetPostListResponseDTO)
def get_post_list_route(
    group_id: int = Query(None),
    crop_id: int = Query(None),
    db: Session = Depends(get_db),
):
    return get_post_list_service(
        GetPostListRequestDTO(group_id=group_id, crop_id=crop_id), db
    )


@post_router.get("/{post_id}", response_model=GetPostDetailResponseDTO)
def get_post_detail_route(post_id: int, db: Session = Depends(get_db)):
    return get_post_detail_service(post_id, db)


@post_router.patch("/{post_id}", response_model=GetPostDetailResponseDTO)
def update_post_route(
    post_id: int, dto: UpdatePostRequestDTO, db: Session = Depends(get_db)
):
    return update_post_service(post_id, dto, db)


@post_router.delete("/{post_id}", response_model=BaseResponseDTO[None])
def delete_post_route(post_id: int, db: Session = Depends(get_db)):
    return delete_post_service(post_id, db)
