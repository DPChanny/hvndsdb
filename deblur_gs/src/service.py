import os
import shutil

from downloader import (
    upload_folder_to_presigned_url,
    upload_file_to_presigned_url,
)

from dto import (
    StartSessionDTO,
    BaseWebSocketDTO,
    UploadCompleteDTO,
    UploadDTO,
    CancelSessionDTO,
    CancelSessionCompleteDTO,
    PLYUrlResponseDTO,
    BaseEndSessionDTO,
)
from envs import TEMP
from globals import get_client
from utils import clean_deblur_gs


def start_session_service(dto: StartSessionDTO):
    if os.path.isdir(os.path.join(TEMP, dto.session_id)):
        shutil.rmtree(os.path.join(TEMP, dto.session_id))

    get_client().start_session(dto.session_id)

    get_client().get_session(dto.session_id).start_deblur_gs_task(
        dto.frames_url, dto.colmap_url, dto.deblur_gs_url
    )


async def cancel_session_service(dto: CancelSessionDTO):
    await get_client().get_session(dto.session_id).cancel_deblur_gs_task()

    await get_client().send(
        BaseWebSocketDTO[CancelSessionCompleteDTO](
            data=CancelSessionCompleteDTO(session_id=dto.session_id)
        )
    )


async def upload_service(dto: UploadDTO):
    if os.path.exists(os.path.join(TEMP, dto.session_id, "deblur_gs")):
        clean_deblur_gs(os.path.join(TEMP, dto.session_id, "deblur_gs"))

        await upload_folder_to_presigned_url(
            dto.deblur_gs_url,
            os.path.join(TEMP, dto.session_id, "deblur_gs"),
            TEMP,
        )

    await get_client().send(
        BaseWebSocketDTO[UploadCompleteDTO](
            data=UploadCompleteDTO(session_id=dto.session_id)
        )
    )


async def ply_url_response_service(dto: PLYUrlResponseDTO):
    ply = await get_client().get_session(dto.session_id).get_ply()

    await upload_file_to_presigned_url(
        dto.ply_url, ply, "application/octet-stream"
    )


def end_session_service(dto: BaseEndSessionDTO):
    get_client().end_session(dto.session_id)
