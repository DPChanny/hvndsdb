from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dtos.building_dto import (
    AddBuildingRequestDTO,
    UpdateBuildingRequestDTO,
    GetBuildingDetailResponseDTO,
    GetBuildingListRequestDTO,
    GetBuildingListResponseDTO,
)
from dtos.base_dto import BaseResponseDTO
from services.building_service import (
    add_building_service,
    get_building_list_service,
    update_building_service,
    delete_building_service,
    get_building_detail_service,
)

building_router = APIRouter()

@building_router.post("/", response_model=GetBuildingDetailResponseDTO)
def add_building_route(dto: AddBuildingRequestDTO, db: Session = Depends(get_db)):
    return add_building_service(dto, db)

@building_router.get("/", response_model=GetBuildingListResponseDTO)
def get_building_list_route(query: str = Query(None), db: Session = Depends(get_db)):
    return get_building_list_service(GetBuildingListRequestDTO(query=query), db)

@building_router.get("/{building_id}", response_model=GetBuildingDetailResponseDTO)
def get_building_detail_route(building_id: UUID, db: Session = Depends(get_db)):
    return get_building_detail_service(building_id, db)

@building_router.patch("/{building_id}", response_model=GetBuildingDetailResponseDTO)
def update_building_route(building_id: UUID, dto: UpdateBuildingRequestDTO, db: Session = Depends(get_db)):
    return update_building_service(building_id, dto, db)

@building_router.delete("/{building_id}", response_model=BaseResponseDTO[None])
def delete_building_route(building_id: UUID, db: Session = Depends(get_db)):
    return delete_building_service(building_id, db)
