import asyncio
import uuid

from dtos.base_dto import BaseWebSocketDTO, BaseEndSessionDTO
from dtos.posenet_dto import FrameDTO
from dtos.unity_dto import SetCameraPositionDTO, SetCameraRotationDTO
from dtos.viewer_dto import FrameCompleteDTO
from utils.s3 import get_presigned_download_url


async def run(client_id, building_id):
    from managers import viewer_manager, unity_manager, posenet_manager
    from managers.viewer_manager import ViewerSession

    client = viewer_manager.get_client(client_id)
    session: ViewerSession = client.get_session(building_id)

    posenet_session_id = "posenet-infer-" + building_id + "-" + uuid.uuid4().hex
    posenet_client_id = await posenet_manager.start_infer_session(
        posenet_session_id, building_id
    )
    posenet_session = posenet_manager.get_client(posenet_client_id).get_session(
        posenet_session_id
    )

    render_session_id = "unity-infer-" + building_id + "-" + uuid.uuid4().hex
    render_client_id = await unity_manager.start_session(render_session_id)

    render_session = unity_manager.get_client(render_client_id).get_session(
        render_session_id
    )

    await render_session.wait_ready()

    ply_url = get_presigned_download_url(building_id + "/point_cloud.ply")
    await render_session.set_ply(ply_url)

    async def update_render_frame_task():
        while True:
            render_frame = await render_session.get_frame()
            if render_frame is None:
                break
            await client.send(
                BaseWebSocketDTO[FrameDTO](
                    data=FrameDTO(
                        session_id=building_id,
                        frame=render_frame,
                    )
                )
            )

    asyncio.create_task(update_render_frame_task())

    await render_session.wait_ready()
    await posenet_session.wait_ready()

    while True:
        infer_frame = await session.get_frame()
        if infer_frame is None:
            break
        await posenet_manager.get_client(posenet_client_id).send(
            BaseWebSocketDTO[FrameDTO](
                data=FrameDTO(session_id=posenet_session_id, frame=infer_frame)
            )
        )
        px, py, pz, rx, ry, rz, rw = await posenet_session.get_6dof()

        await unity_manager.get_client(render_client_id).send(
            BaseWebSocketDTO[SetCameraPositionDTO](
                data=SetCameraPositionDTO(
                    session_id=render_session_id, x=px, y=py, z=pz
                )
            )
        )
        await unity_manager.get_client(render_client_id).send(
            BaseWebSocketDTO[SetCameraRotationDTO](
                data=SetCameraRotationDTO(
                    session_id=render_session_id, x=rx, y=ry, z=rz, w=rw
                )
            )
        )

        await client.send(
            BaseWebSocketDTO[FrameCompleteDTO](
                data=FrameCompleteDTO(session_id=building_id)
            )
        )

    await unity_manager.get_client(render_client_id).end_session(
        render_session_id,
        BaseWebSocketDTO[BaseEndSessionDTO](
            data=BaseEndSessionDTO(session_id=render_session_id)
        ),
    )
    await posenet_manager.get_client(posenet_client_id).end_session(
        posenet_session_id,
        BaseWebSocketDTO[BaseEndSessionDTO](
            data=BaseEndSessionDTO(session_id=posenet_session_id)
        ),
    )
