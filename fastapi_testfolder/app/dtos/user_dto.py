from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin
from uuid import UUID

class UserDTO(BaseModel):
    user_id: UUID
    email: str
    name: str

class UserBaseDTO(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

class AddUserRequestDTO(UserBaseDTO):
    email: str
    name: str

class UpdateUserRequestDTO(UserBaseDTO):
    pass

class GetUserDetailResponseDTO(BaseResponseDTO[UserDTO]):
    pass

class GetUserListRequestDTO(BaseModel):
    query: Optional[str] = None

class GetUserListResponseDTO(BaseResponseDTO[List[UserDTO]]):
    pass