import asyncio

from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import CancelSessionDTO, StartSessionDTO
from managers.web_socket_manager import (
    WebSocketManager,
    WebsocketClient,
    WebsocketSession,
)
from utils.s3 import get_presigned_download_url, is_key_exists


class DeblurGSClient(WebsocketClient):
    def get_session_count(self) -> int:
        return len(self._sessions)

    async def start_session(
            self, building_id: str, dto: BaseWebSocketDTO[StartSessionDTO]
    ):
        await super().start_session(building_id, dto)

    async def cancel_session(self, building_id: str):
        await self.get_session(building_id).put_progress(None)
        await self.send(
            BaseWebSocketDTO[CancelSessionDTO](
                data=CancelSessionDTO(session_id=building_id)
            ),
        )

    async def end_session(self, building_id: str, dto: BaseWebSocketDTO):
        await self.get_session(building_id).put_progress(None)
        await super().end_session(building_id, dto)


class DeblurGSSession(WebsocketSession):
    def __init__(self, session_id: str, client: DeblurGSClient):
        super().__init__(session_id, client)
        self._progress: asyncio.Queue = asyncio.Queue()
        self.set_ready()

    async def put_progress(self, progress: str | None):
        await self._progress.put(progress)

    async def get_progress(self):
        return await self._progress.get()


class DeblurGSManager(WebSocketManager):
    def __init__(self):
        super().__init__(DeblurGSClient, DeblurGSSession)

    def get_client(self, client_id: str) -> DeblurGSClient:
        return super().get_client(client_id)

    async def start_session(self, building_id: str) -> str:
        if not self._clients:
            raise LookupError("No clients connected")

        selected_client_id = next(iter(self._clients.keys()))
        for client_id in self._clients.keys():
            if self.get_client(client_id).has_session(building_id):
                return client_id

            if (
                    self.get_client(client_id).get_session_count()
                    < self.get_client(selected_client_id).get_session_count()
            ):
                selected_client_id = client_id

        await self.get_client(selected_client_id).start_session(
            building_id,
            BaseWebSocketDTO[StartSessionDTO](
                data=StartSessionDTO(
                    session_id=building_id,
                    frames_url=get_presigned_download_url(
                        building_id + "/frames.zip"
                    ),
                    colmap_url=get_presigned_download_url(
                        building_id + "/colmap.zip"
                    ),
                    deblur_gs_url=(
                        get_presigned_download_url(
                            building_id + "/deblur_gs.zip"
                        )
                        if is_key_exists(building_id + "/deblur_gs.zip")
                        else None
                    ),
                ),
            ),
        )

        return selected_client_id

    async def cancel_session(self, building_id: str):
        for client in self._clients.values():
            if client.has_session(building_id):
                await client.cancel_session(building_id)
                return

        raise LookupError(f"No session found {building_id}")
