import os
import shutil

from downloader import (
    upload_folder_to_presigned_url,
)

from dto import (
    BaseWebSocketDTO,
    UploadCompleteDTO,
    UploadDTO,
    CancelSessionDTO,
    CancelSessionCompleteDTO,
    BaseEndSessionDTO,
    FrameDTO,
    StartTrainDTO,
    StartTrainSessionDTO,
    StartInferSessionDTO,
    BaseStartSessionDTO,
)
from envs import TEMP
from globals import get_client
from utils import clean_posenet


def start_session_service(dto: BaseStartSessionDTO):
    if os.path.isdir(os.path.join(TEMP, dto.session_id)):
        shutil.rmtree(os.path.join(TEMP, dto.session_id))

    get_client().start_session(dto.session_id)


def start_train_session_service(dto: StartTrainSessionDTO):
    start_session_service(dto)

    get_client().get_session(dto.session_id).start_train_download_task(
        dto.frames_url, dto.colmap_url, dto.posenet_url
    )


def start_infer_session_service(dto: StartInferSessionDTO):
    start_session_service(dto)

    get_client().get_session(dto.session_id).start_infer_download_task(
        dto.posenet_url
    )


def start_train_service(dto: StartTrainDTO):
    get_client().get_session(dto.session_id).start_train_task()


async def cancel_session_service(dto: CancelSessionDTO):
    await get_client().get_session(dto.session_id).cancel_posenet()

    await get_client().send(
        BaseWebSocketDTO[CancelSessionCompleteDTO](
            data=CancelSessionCompleteDTO(session_id=dto.session_id)
        )
    )


async def upload_service(dto: UploadDTO):
    posenet_path = os.path.join(TEMP, dto.session_id, "posenet")
    if os.path.isdir(posenet_path) and len(os.listdir(posenet_path)) != 0:
        clean_posenet(posenet_path)

        await upload_folder_to_presigned_url(
            dto.posenet_url, posenet_path, TEMP
        )

    await get_client().send(
        BaseWebSocketDTO[UploadCompleteDTO](
            data=UploadCompleteDTO(session_id=dto.session_id)
        )
    )


async def frame_service(dto: FrameDTO):
    await get_client().get_session(dto.session_id).infer_frame(dto.frame)


def end_session_service(dto: BaseEndSessionDTO):
    get_client().end_session(dto.session_id)
