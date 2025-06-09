from sqlalchemy.orm import Session
from dtos.building_dto import (
    AddBuildingRequestDTO,
    BuildingDetailDTO,
    UpdateBuildingRequestDTO,
    BuildingDTO,
    GetBuildingDetailResponseDTO,
    GetBuildingListRequestDTO,
    GetBuildingListResponseDTO,
)
from managers import analyzer_manager
from utils.exception import CustomException, handle_exception
from dtos.base_dto import BaseResponseDTO
from entities.building import Building
from utils.s3 import get_presigned_upload_url, is_key_exists


def get_building_detail_service(building_id: str, db: Session):
    try:
        building = (
            db.query(Building)
            .filter(Building.building_id == building_id)
            .first()
        )
        if not building:
            raise CustomException(404, "Building not found.")
        dto = BuildingDetailDTO(
            name=building.name,
            building_id=building.building_id,
            longitude=building.longitude,
            latitude=building.latitude,
            created_at=building.created_at,
            updated_at=building.updated_at,
            sample=is_key_exists(building_id + "/sample.mp4"),
            frames=is_key_exists(building_id + "/frames.zip"),
            colmap=is_key_exists(building_id + "/colmap.zip"),
            deblur_gs=is_key_exists(building_id + "/deblur_gs.zip"),
            ply=is_key_exists(building_id + "/point_cloud.ply"),
            analyzing=analyzer_manager.has_analyzer_task(building_id),
            posenet=is_key_exists(building_id + "/posenet.zip"),
        )

        return GetBuildingDetailResponseDTO(
            success=True,
            code=200,
            message="Building detail retrieved.",
            data=dto,
        )
    except Exception as e:
        handle_exception(e, db)


def add_building_service(dto: AddBuildingRequestDTO, db: Session):
    try:
        building = Building(
            name=dto.name,
            latitude=dto.latitude,
            longitude=dto.longitude,
        )
        db.add(building)
        db.commit()
        db.refresh(building)
        return get_building_detail_service(building.building_id, db)
    except Exception as e:
        handle_exception(e, db)


def get_building_list_service(dto: GetBuildingListRequestDTO, db: Session):
    try:
        query = db.query(Building)
        if dto.query:
            query = query.filter(Building.name.contains(dto.query))
        buildings = query.all()
        building_dtos = [
            BuildingDTO.model_validate(building) for building in buildings
        ]
        return GetBuildingListResponseDTO(
            success=True,
            code=200,
            message="Building list retrieved.",
            data=building_dtos,
        )
    except Exception as e:
        handle_exception(e, db)


def update_building_service(
        building_id: str, dto: UpdateBuildingRequestDTO, db: Session
):
    try:
        building = (
            db.query(Building)
            .filter(Building.building_id == building_id)
            .first()
        )
        if not building:
            raise CustomException(404, "Building not found.")
        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(building, key, value)
        db.commit()
        db.refresh(building)
        return get_building_detail_service(building.building_id, db)
    except Exception as e:
        handle_exception(e, db)


def delete_building_service(building_id: str, db: Session):
    try:
        building = (
            db.query(Building)
            .filter(Building.building_id == building_id)
            .first()
        )
        if not building:
            raise CustomException(404, "Building not found.")
        db.delete(building)
        db.commit()
        return BaseResponseDTO(
            success=True, code=200, message="Building deleted.", data=None
        )
    except Exception as e:
        handle_exception(e, db)


def get_sample_url_service(building_id: str):
    try:
        return BaseResponseDTO[str](
            success=True,
            code=201,
            message="Sample upload URL generated.",
            data=get_presigned_upload_url(
                f"{building_id}/sample.mp4", "video/mp4"
            ),
        )
    except Exception as e:
        raise CustomException(500, f"Error generating upload URL: {str(e)}")
