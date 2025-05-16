from fastapi import APIRouter, HTTPException
from ..models.user import BuildingCreate, BuildingRead
from uuid import UUID

router = APIRouter(prefix="/api/building", tags=["Building"])

@router.post("", response_model=BuildingRead)
def create_building(building: BuildingCreate):
    # 실제 DB 저장 로직 필요
    return BuildingRead(building_id=UUID("00000000-0000-0000-0000-000000000000"), **building.dict())

@router.get("", response_model=list[BuildingRead])
def list_buildings():
    # 실제 DB 조회 로직 필요
    return []

@router.patch("/{building_id}", response_model=BuildingRead)
def update_building(building_id: UUID, building: BuildingCreate):
    # 실제 DB 수정 로직 필요
    return BuildingRead(building_id=building_id, **building.dict())

@router.delete("/{building_id}")
def delete_building(building_id: UUID):
    # 실제 DB 삭제 로직 필요
    return {"ok": True}

@router.get("/{building_id}/{user_id}", response_model=BuildingRead)
def get_building_for_user(building_id: UUID, user_id: UUID):
    # 실제 DB 조회 로직 필요
    return BuildingRead(building_id=building_id, user_id=user_id, name="", address="", is_ready=False, s3_url=None)
