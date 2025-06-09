from dtos.base_dto import (
    BaseWebSocketDTO,
    BaseEndSessionDTO,
    BaseSessionReadyDTO,
)
from dtos.posenet_dto import (
    ProgressDTO,
    UploadDTO,
    CancelSessionCompleteDTO,
    UploadCompleteDTO,
    CompleteDTO,
    SixDOFDTO,
)
from managers import posenet_manager
from managers.posenet_manager import PosenetSession
from utils.s3 import get_presigned_upload_url


async def upload_service(client_id: str, building_id: str):
    await posenet_manager.get_client(client_id).send(
        BaseWebSocketDTO[UploadDTO](
            data=UploadDTO(
                session_id=building_id,
                posenet_url=get_presigned_upload_url(
                    building_id + "/posenet.zip",
                    "application/zip",
                ),
            ),
        ),
    )


async def six_dof_service(client_id: str, dto: SixDOFDTO):
    session: PosenetSession = posenet_manager.get_client(client_id).get_session(
        dto.session_id
    )
    await session.put_6dof(
        (dto.px, dto.py, dto.pz, dto.rx, dto.ry, dto.rz, dto.rw)
    )


async def complete_service(client_id: str, dto: CompleteDTO):
    await upload_service(client_id, dto.session_id)


async def upload_complete_service(client_id: str, dto: UploadCompleteDTO):
    await posenet_manager.get_client(client_id).end_session(
        dto.session_id,
        BaseWebSocketDTO[BaseEndSessionDTO](
            data=BaseEndSessionDTO(session_id=dto.session_id)
        ),
    )


async def progress_service(client_id: str, dto: ProgressDTO):
    session: PosenetSession = posenet_manager.get_client(client_id).get_session(
        dto.session_id
    )
    await session.put_progress(dto.progress)


async def cancel_complete_service(
        client_id: str, dto: CancelSessionCompleteDTO
):
    await upload_service(client_id, dto.session_id)


def session_ready_service(client_id: str, dto: BaseSessionReadyDTO):
    posenet_manager.get_client(client_id).get_session(
        dto.session_id
    ).set_ready()
