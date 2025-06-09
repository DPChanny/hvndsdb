import asyncio
import os
import shutil
import uuid

from fastapi.logger import logger

from dtos.base_dto import BaseEndSessionDTO, BaseWebSocketDTO
from dtos.posenet_dto import StartTrainDTO
from tasks import (
    frames_task,
    colmap_task,
    update_center_transform_task,
    update_around_transform_task,
)
from utils.envs import TEMP
from utils.s3 import (
    get_last_modified,
    get_presigned_download_url,
    get_presigned_upload_url,
    is_key_exists,
)


async def run(building_id: str):
    from managers import (
        deblur_gs_manager,
        unity_manager,
        analyzer_manager,
        posenet_manager,
    )

    FRAMES = not is_key_exists(building_id + "/frames.zip")
    COLMAP = not is_key_exists(building_id + "/colmap.zip")

    if os.path.isdir(os.path.join(TEMP, building_id)):
        shutil.rmtree(os.path.join(TEMP, building_id))

    if FRAMES:
        if await frames_task.run(
                building_id,
                get_presigned_download_url(building_id + "/sample.mp4"),
                get_presigned_upload_url(
                    building_id + "/frames.zip",
                    "application/zip",
                ),
        ):
            await analyzer_manager.update_progress(
                building_id, "Frames extraction failed."
            )
            return

    if COLMAP:
        if await colmap_task.run(
                building_id,
                get_presigned_upload_url(
                    building_id + "/colmap.zip",
                    "application/zip",
                ),
                (
                        get_presigned_download_url(building_id + "/frames.zip")
                        if not FRAMES
                        else None
                ),
        ):
            await analyzer_manager.update_progress(
                building_id, "COLMAP extraction failed."
            )
            return

    try:
        deblur_gs_client_id = await deblur_gs_manager.start_session(building_id)
        deblur_gs_session = deblur_gs_manager.get_client(
            deblur_gs_client_id
        ).get_session(building_id)

        posenet_client_id = await posenet_manager.start_train_session(
            building_id
        )
        posenet_session = posenet_manager.get_client(
            posenet_client_id
        ).get_session(building_id)

        center_session_id = (
                "unity-center-" + building_id + "-" + uuid.uuid4().hex
        )
        around_session_id = (
                "unity-around-" + building_id + "-" + uuid.uuid4().hex
        )
        center_client_id = await unity_manager.start_session(center_session_id)
        around_client_id = await unity_manager.start_session(around_session_id)
        center_session = unity_manager.get_client(center_client_id).get_session(
            center_session_id
        )
        around_session = unity_manager.get_client(around_client_id).get_session(
            around_session_id
        )

        async def update_deblur_gs_progress():
            while True:
                progress = await deblur_gs_session.get_progress()
                if progress is None:
                    break
                await analyzer_manager.update_deblur_gs_progress(
                    building_id, progress
                )

        async def update_posenet_progress():
            while True:
                progress = await posenet_session.get_progress()
                if progress is None:
                    break
                await analyzer_manager.update_posenet_progress(
                    building_id, progress
                )

        async def update_center_frame():
            while True:
                frame = await center_session.get_frame()
                if frame is None:
                    break
                await analyzer_manager.update_center_frame(building_id, frame)

        async def update_around_frame():
            while True:
                frame = await around_session.get_frame()
                if frame is None:
                    break
                await analyzer_manager.update_around_frame(building_id, frame)

        async def update_unity_ply():
            await center_session.wait_ready()
            await around_session.wait_ready()
            try:
                last_last_modified = None
                while True:
                    last_modified = get_last_modified(
                        building_id + "/point_cloud.ply"
                    )
                    if last_modified != last_last_modified:
                        last_last_modified = last_modified
                        ply_url = get_presigned_download_url(
                            building_id + "/point_cloud.ply"
                        )
                        await center_session.set_ply(ply_url)
                        await around_session.set_ply(ply_url)
                    await asyncio.sleep(1)

            except asyncio.CancelledError:
                raise

        asyncio.create_task(update_deblur_gs_progress())
        asyncio.create_task(update_posenet_progress())
        asyncio.create_task(update_center_frame())
        asyncio.create_task(update_around_frame())
        session_update_center_transform_task = asyncio.create_task(
            update_center_transform_task.run(
                center_client_id, center_session_id
            )
        )
        session_update_around_transform_task = asyncio.create_task(
            update_around_transform_task.run(
                around_client_id, around_session_id
            )
        )
        update_unity_ply_task = asyncio.create_task(update_unity_ply())

        await deblur_gs_session.wait_ready()
        await posenet_session.wait_ready()

        await posenet_manager.get_client(posenet_client_id).send(
            BaseWebSocketDTO[StartTrainDTO](
                data=StartTrainDTO(session_id=building_id)
            )
        )

        await deblur_gs_session.wait_ended()
        await posenet_session.wait_ended()

        session_update_center_transform_task.cancel()
        try:
            await session_update_center_transform_task
        except asyncio.CancelledError:
            pass

        session_update_around_transform_task.cancel()
        try:
            await session_update_around_transform_task
        except asyncio.CancelledError:
            pass

        update_unity_ply_task.cancel()
        try:
            await update_unity_ply_task
        except asyncio.CancelledError:
            pass

        await unity_manager.get_client(center_client_id).end_session(
            center_session_id,
            BaseWebSocketDTO[BaseEndSessionDTO](
                data=BaseEndSessionDTO(session_id=center_session_id)
            ),
        )
        await unity_manager.get_client(around_client_id).end_session(
            around_session_id,
            BaseWebSocketDTO[BaseEndSessionDTO](
                data=BaseEndSessionDTO(session_id=around_session_id)
            ),
        )

    except Exception as e:
        logger.error(f"Analyzer worker failed {e}")

    logger.info("Analyzer worker finished.")
