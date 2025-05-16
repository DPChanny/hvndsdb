from typing import Optional
from sqlalchemy.orm import Session
from entities.comment import Comment
from entities.post import Post
from dtos.comment_dto import (
    CommentDTO,
    CommentDetailDTO,
    AddCommentRequestDTO,
    GetCommentListRequestDTO,
    UpdateCommentRequestDTO,
    GetCommentDetailResponseDTO,
    GetCommentListResponseDTO,
)
from dtos.base_dto import BaseResponseDTO
from exception import CustomException, handle_exception


def get_comment_detail_service(
    comment_id: int, db: Session
) -> GetCommentDetailResponseDTO:
    try:
        comment = (
            db.query(Comment).filter(Comment.comment_id == comment_id).first()
        )
        if not comment:
            raise CustomException(404, "Comment not found.")

        return GetCommentDetailResponseDTO(
            success=True,
            code=200,
            message="Comment detail retrieved successfully.",
            data=CommentDetailDTO.model_validate(comment),
        )

    except Exception as e:
        handle_exception(e, db)


def add_comment_service(
    dto: AddCommentRequestDTO, db: Session
) -> GetCommentDetailResponseDTO:
    try:
        post = db.query(Post).filter(Post.post_id == dto.post_id).first()
        if not post:
            raise CustomException(404, "Post not found.")

        comment = Comment(
            post_id=dto.post_id,
            content=dto.content,
            author=dto.author,
        )
        db.add(comment)
        db.commit()

        return get_comment_detail_service(comment.comment_id, db)

    except Exception as e:
        handle_exception(e, db)


def get_comment_list_service(
    dto: GetCommentListRequestDTO, db: Session
) -> GetCommentListResponseDTO:
    try:
        query = db.query(Comment)
        if dto.post_id:
            query = query.filter(Comment.post_id == dto.post_id)

        comment_entities = query.all()
        comment_dtos = [CommentDTO.model_validate(c) for c in comment_entities]

        return GetCommentListResponseDTO(
            success=True,
            code=200,
            message="Comment list retrieved successfully.",
            data=comment_dtos,
        )

    except Exception as e:
        handle_exception(e, db)


def update_comment_service(
    comment_id: int, dto: UpdateCommentRequestDTO, db: Session
) -> GetCommentDetailResponseDTO:
    try:
        comment = (
            db.query(Comment).filter(Comment.comment_id == comment_id).first()
        )
        if not comment:
            raise CustomException(404, "Comment not found.")

        comment.content = dto.content
        db.commit()

        return get_comment_detail_service(comment.comment_id, db)

    except Exception as e:
        handle_exception(e, db)


def delete_comment_service(
    comment_id: int, db: Session
) -> BaseResponseDTO[None]:
    try:
        comment = (
            db.query(Comment).filter(Comment.comment_id == comment_id).first()
        )
        if not comment:
            raise CustomException(404, "Comment not found.")

        db.delete(comment)
        db.commit()

        return BaseResponseDTO(
            success=True,
            code=200,
            message="Comment deleted successfully.",
            data=None,
        )

    except Exception as e:
        handle_exception(e, db)
