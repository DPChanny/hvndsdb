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


def get_group_detail_service(
    group_id: int, db: Session
) -> GetGroupDetailResponseDTO:
    try:
        group = (
            db.query(Group)
            .options(
                joinedload(Group.crops).joinedload(Crop.posts),
                joinedload(Group.crops).joinedload(Crop.sensors),
                joinedload(Group.crops).joinedload(Crop.schedules),
            )
            .filter(Group.group_id == group_id)
            .first()
        )

        if not group:
            raise CustomException(404, "Group not found.")

        return GetGroupDetailResponseDTO(
            success=True,
            code=200,
            message="Group detail retrieved successfully.",
            data=GroupDetailDTO.model_validate(group),
        )

    except Exception as e:
        handle_exception(e, db)


def add_group_service(
    dto: AddGroupRequestDTO, db: Session
) -> GetGroupDetailResponseDTO:
    try:
        group = Group(name=dto.name, location=dto.location)
        db.add(group)
        db.commit()

        return get_group_detail_service(group.group_id, db)

    except Exception as e:
        handle_exception(e, db)


def get_group_list_service(
    dto: GetGroupListRequestDTO, db: Session
) -> GetGroupListResponseDTO:
    try:
        query = db.query(Group)
        if dto.name:
            query = query.filter(Group.name.contains(dto.name))
        if dto.location:
            query = query.filter(Group.location.contains(dto.location))

        group_entities = query.all()
        group_dtos = [GroupDTO.model_validate(g) for g in group_entities]

        return GetGroupListResponseDTO(
            success=True,
            code=200,
            message="Group list retrieved successfully.",
            data=group_dtos,
        )

    except Exception as e:
        handle_exception(e, db)


def update_group_service(
    group_id: int, dto: UpdateGroupRequestDTO, db: Session
) -> GetGroupDetailResponseDTO:
    try:
        group = db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            raise CustomException(1404, "Group not found")

        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(group, key, value)

        db.commit()

        return get_group_detail_service(group.group_id, db)

    except Exception as e:
        handle_exception(e, db)


def delete_group_service(group_id: int, db: Session) -> BaseResponseDTO[None]:
    try:
        group = db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            raise CustomException(404, "Group not found.")

        db.delete(group)
        db.commit()

        return BaseResponseDTO(
            success=True,
            code=200,
            message="Group and all related entities deleted successfully.",
            data=None,
        )

    except Exception as e:
        handle_exception(e, db)
