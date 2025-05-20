from sqlalchemy.orm import Session, joinedload

from dtos.group_dto import (
    AddGroupRequestDTO,
    GetGroupListRequestDTO,
    GetGroupListResponseDTO,
    GetGroupDetailResponseDTO,
    GroupDTO,
    GroupDetailDTO,
    UpdateGroupRequestDTO,
)
from entities.group import Group
from entities.crop import Crop
from exception import CustomException, handle_exception
from dtos.base_dto import BaseResponseDTO

def add_user_service(dto, db):
    # 유저 추가 로직
    pass

def get_user_list_service(query, db):
    # 유저 목록 조회 로직
    pass

def update_user_service(user_id, dto, db):
    # 유저 정보 수정 로직
    pass

def delete_user_service(user_id, db):
    # 유저 삭제 로직
    pass 