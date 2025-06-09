import asyncio
import uuid

from dtos.unity_dto import SetCameraPositionDTO, SetCameraRotationDTO
from dtos.viewer_dto import FrameDTO, FrameCompleteDTO
from dtos.base_dto import BaseWebSocketDTO

from managers.web_socket_manager import (
    WebSocketManager,
    WebsocketSession,
    WebsocketClient,
)


class ViewerClient(WebsocketClient):
    async def update_frame(self, session_id: str, frame: str):
        await self.send(
            BaseWebSocketDTO[FrameDTO](
                data=FrameDTO(session_id=session_id, frame=frame)
            )
        )


class ViewerSession(WebsocketSession):
    def __init__(self, session_id: str, client: ViewerClient):
        super().__init__(session_id, client)
        from managers.unity_manager import UnitySession

        self._render_session: UnitySession | None = None
        self._render_client_id = None
        self._render_session_id = None
        from managers.posenet_manager import PosenetSession

        self._posenet_session: PosenetSession | None = None
        self._posenet_client_id = None
        self._posenet_session_id = None

        async def update_frame_task():
            while True:
                frame = await self._render_session.get_frame()
                if frame is None:
                    break
                await self._client.send(
                    BaseWebSocketDTO[FrameDTO](
                        data=FrameDTO(
                            session_id=self._session_id,
                            frame=frame,
                        )
                    )
                )

        asyncio.create_task(update_frame_task())

    async def init_internal_session(self, building_id):
        from managers import unity_manager
        from managers import posenet_manager

        self._posenet_session_id = (
                "posenet-infer-" + building_id + "-" + uuid.uuid4().hex
        )
        self._posenet_client_id = await posenet_manager.start_infer_session(
            self._posenet_session_id, building_id
        )
        self._posenet_session = posenet_manager.get_client(
            self._posenet_client_id
        ).get_session(self._posenet_session_id)

        self._render_session_id = (
                "unity-center-" + building_id + "-" + uuid.uuid4().hex
        )
        self._render_client_id = await unity_manager.start_session(
            self._render_session_id
        )

        self._render_session = unity_manager.get_client(
            self._render_client_id
        ).get_session(self._render_session_id)

        await self._render_session.wait_ready()

        from utils.s3 import get_presigned_download_url

        ply_url = get_presigned_download_url(building_id + "/point_cloud.ply")
        await self._render_session.set_ply(ply_url)

    async def infer_frame(self, frame: str):
        from managers import posenet_manager

        await self._render_session.wait_ready()
        await self._posenet_session.wait_ready()

        await posenet_manager.get_client(self._posenet_client_id).send(
            BaseWebSocketDTO[FrameDTO](
                data=FrameDTO(session_id=self._posenet_session_id, frame=frame)
            )
        )
        px, py, pz, rx, ry, rz, rw = await self._posenet_session.get_6dof()
        from managers import unity_manager

        await unity_manager.get_client(self._render_client_id).send(
            BaseWebSocketDTO[SetCameraPositionDTO](
                data=SetCameraPositionDTO(
                    session_id=self._render_session_id, x=px, y=py, z=pz
                )
            )
        )
        await unity_manager.get_client(self._render_client_id).send(
            BaseWebSocketDTO[SetCameraRotationDTO](
                data=SetCameraRotationDTO(
                    session_id=self._render_session_id, x=rx, y=ry, z=rz, w=rw
                )
            )
        )

        await self._client.send(
            BaseWebSocketDTO[FrameCompleteDTO](
                data=FrameCompleteDTO(session_id=self._session_id)
            )
        )


class ViewerManager(WebSocketManager):
    def __init__(self):
        super().__init__(ViewerClient, ViewerSession)
