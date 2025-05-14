from fastapi import APIRouter, HTTPException
from ..models.user import UserCreate, UserRead
from uuid import UUID

router = APIRouter(prefix="/api/user", tags=["User"])

@router.post("", response_model=UserRead)
def create_user(user: UserCreate):
    # 실제 DB 저장 로직 필요
    return UserRead(user_id=UUID("00000000-0000-0000-0000-000000000000"), **user.dict())

@router.get("", response_model=list[UserRead])
def list_users():
    # 실제 DB 조회 로직 필요
    return []

@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: UUID, user: UserCreate):
    # 실제 DB 수정 로직 필요
    return UserRead(user_id=user_id, **user.dict())

@router.delete("/{user_id}")
def delete_user(user_id: UUID):
    # 실제 DB 삭제 로직 필요
    return {"ok": True} 