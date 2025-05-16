from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dtos.base_dto import BaseResponseDTO
from dtos.comment_dto import (
    AddCommentRequestDTO,
    GetCommentDetailResponseDTO,
    GetCommentListRequestDTO,
    GetCommentListResponseDTO,
    UpdateCommentRequestDTO,
)
from services.comment_service import (
    add_comment_service,
    get_comment_detail_service,
    get_comment_list_service,
    update_comment_service,
    delete_comment_service,
)

comment_router = APIRouter()


@comment_router.post("/", response_model=GetCommentDetailResponseDTO)
def add_comment_route(dto: AddCommentRequestDTO, db: Session = Depends(get_db)):
    return add_comment_service(dto, db)


@comment_router.get("/", response_model=GetCommentListResponseDTO)
def get_comment_list_route(
    post_id: int = Query(None), db: Session = Depends(get_db)
):
    return get_comment_list_service(
        GetCommentListRequestDTO(post_id=post_id), db
    )


@comment_router.get("/{comment_id}", response_model=GetCommentDetailResponseDTO)
def get_comment_detail_route(comment_id: int, db: Session = Depends(get_db)):
    return get_comment_detail_service(comment_id, db)


@comment_router.patch(
    "/{comment_id}", response_model=GetCommentDetailResponseDTO
)
def update_comment_route(
    comment_id: int, dto: UpdateCommentRequestDTO, db: Session = Depends(get_db)
):
    return update_comment_service(comment_id, dto, db)


@comment_router.delete("/{comment_id}", response_model=BaseResponseDTO[None])
def delete_comment_route(comment_id: int, db: Session = Depends(get_db)):
    return delete_comment_service(comment_id, db)
