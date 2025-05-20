from sqlalchemy.orm import Session
from dtos.building_dto import (
    AddBuildingRequestDTO,
    UpdateBuildingRequestDTO,
    BuildingDTO,
    GetBuildingDetailResponseDTO,
    GetBuildingListRequestDTO,
    GetBuildingListResponseDTO,
)
from exception import CustomException, handle_exception
from dtos.base_dto import BaseResponseDTO
from entities.building import Building
from uuid import UUID

from entities.building import Building, BuildingType
from entities.user import User


def get_building_detail_service(building_id: UUID, db: Session) -> GetBuildingDetailResponseDTO:
    try:
        building = db.query(Building).filter(Building.building_id == building_id).first()
        if not building:
            raise CustomException(404, "Building not found.")
        dto = BuildingDTO(
            building_id=building.building_id,
            name=building.name,
            address=building.address,
            user_id=building.user_id,
            is_ready=building.is_ready,
            s3_url=building.s3_url
        )
        return GetBuildingDetailResponseDTO(
            success=True, code=200, message="Building detail retrieved.", data=dto
        )
    except Exception as e:
        handle_exception(e, db)

def add_building_service(dto: AddBuildingRequestDTO, db: Session) -> GetBuildingDetailResponseDTO:
    try:
        building = Building(
            name=dto.name,
            address=dto.address,
            user_id=dto.user_id,
            is_ready=dto.is_ready if dto.is_ready is not None else False,
            s3_url=dto.s3_url
        )
        db.add(building)
        db.commit()
        db.refresh(building)
        return get_building_detail_service(building.building_id, db)
    except Exception as e:
        handle_exception(e, db)

def get_building_list_service(dto: GetBuildingListRequestDTO, db: Session) -> GetBuildingListResponseDTO:
    try:
        query = db.query(Building)
        if dto.query:
            query = query.filter(Building.name.contains(dto.query))
        buildings = query.all()
        dtos = [
            BuildingDTO(
                building_id=b.building_id,
                name=b.name,
                address=b.address,
                user_id=b.user_id,
                is_ready=b.is_ready,
                s3_url=b.s3_url
            ) for b in buildings
        ]
        return GetBuildingListResponseDTO(
            success=True, code=200, message="Building list retrieved.", data=dtos
        )
    except Exception as e:
        handle_exception(e, db)

def update_building_service(building_id: UUID, dto: UpdateBuildingRequestDTO, db: Session) -> GetBuildingDetailResponseDTO:
    try:
        building = db.query(Building).filter(Building.building_id == building_id).first()
        if not building:
            raise CustomException(404, "Building not found.")
        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(building, key, value)
        db.commit()
        db.refresh(building)
        return get_building_detail_service(building.building_id, db)
    except Exception as e:
        handle_exception(e, db)

def delete_building_service(building_id: UUID, db: Session) -> BaseResponseDTO[None]:
    try:
        building = db.query(Building).filter(Building.building_id == building_id).first()
        if not building:
            raise CustomException(404, "Building not found.")
        db.delete(building)
        db.commit()
        return BaseResponseDTO(
            success=True, code=200, message="Building deleted.", data=None
        )
    except Exception as e:
        handle_exception(e, db)

def get_building_user_service(building_id: int, user_id: int, db: Session) -> BuildingDTO:
    # 특정 빌딩-유저 정보 조회 로직
    pass
