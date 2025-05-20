from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin
from uuid import UUID

# (1) 빌딩 정보 DTO
class BuildingDTO(BaseModel):
    building_id: int
    user_id: int
    building_type: Optional[str] = None

class BuildingBaseDTO(BaseModel):
    user_id: Optional[int] = None
    building_type: Optional[str] = None
    # address: Optional[str] = None

# (2) 빌딩 추가 요청 DTO
class AddBuildingRequestDTO(BuildingBaseDTO):
    user_id: int
    building_type: str

class UpdateBuildingRequestDTO(BuildingBaseDTO):
    pass

# (3) 빌딩 상세 조회 응답 DTO
class GetBuildingDetailResponseDTO(BaseResponseDTO[BuildingDTO]):
    pass

# (4) 빌딩 목록 조회 요청/응답 DTO
class GetBuildingListRequestDTO(BaseModel):
    query: Optional[str] = None

class GetBuildingListResponseDTO(BaseResponseDTO[List[BuildingDTO]]):
    pass