from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from dtos.crop_dto import (
    AddCropRequestDTO,
    GetCropDetailResponseDTO,
    GetCropListRequestDTO,
    GetCropListResponseDTO,
    CropDTO,
    CropDetailDTO,
    UpdateCropRequestDTO,
)
from entities.crop import Crop
from entities.group import Group
from exception import CustomException, handle_exception
from dtos.base_dto import BaseResponseDTO


def get_crop_detail_service(
    crop_id: int, db: Session
) -> GetCropDetailResponseDTO:
    try:
        crop = (
            db.query(Crop)
            .options(
                joinedload(Crop.posts),
                joinedload(Crop.schedules),
                joinedload(Crop.sensors),
            )
            .filter(Crop.crop_id == crop_id)
            .first()
        )

        if not crop:
            raise CustomException(404, "Crop not found.")

        return GetCropDetailResponseDTO(
            success=True,
            code=200,
            message="Crop detail retrieved successfully.",
            data=CropDetailDTO.model_validate(crop),
        )

    except Exception as e:
        handle_exception(e, db)


def add_crop_service(
    dto: AddCropRequestDTO, db: Session
) -> GetCropDetailResponseDTO:
    try:
        group = db.query(Group).filter(Group.group_id == dto.group_id).first()
        if not group:
            raise CustomException(404, "Group not found.")

        crop = Crop(
            group_id=dto.group_id, name=dto.name, crop_type=dto.crop_type
        )
        db.add(crop)
        db.commit()

        return get_crop_detail_service(crop.crop_id, db)

    except Exception as e:
        handle_exception(e, db)


def get_crop_list_service(
    dto: GetCropListRequestDTO, db: Session
) -> GetCropListResponseDTO:
    try:
        query = db.query(Crop)

        if dto.group_id:
            query = query.filter(Crop.group_id == dto.group_id)

        crop_entities = query.all()
        crop_dtos = [CropDTO.model_validate(crop) for crop in crop_entities]

        return GetCropListResponseDTO(
            success=True,
            code=200,
            message="Crop list retrieved successfully.",
            data=crop_dtos,
        )

    except Exception as e:
        handle_exception(e, db)


def update_crop_service(
    crop_id: int, dto: UpdateCropRequestDTO, db: Session
) -> GetCropDetailResponseDTO:
    try:
        crop = db.query(Crop).filter(Crop.crop_id == crop_id).first()
        if not crop:
            raise CustomException(404, "Crop not found.")

        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(crop, key, value)

        db.commit()

        return get_crop_detail_service(crop.crop_id, db)

    except Exception as e:
        handle_exception(e, db)


def delete_crop_service(crop_id: int, db: Session) -> BaseResponseDTO[None]:
    try:
        crop = db.query(Crop).filter(Crop.crop_id == crop_id).first()
        if not crop:
            raise CustomException(404, "Crop not found.")

        db.delete(crop)
        db.commit()

        return BaseResponseDTO(
            success=True,
            code=200,
            message="Crop and all related data deleted successfully.",
            data=None,
        )

    except Exception as e:
        handle_exception(e, db)
