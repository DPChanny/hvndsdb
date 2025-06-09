import asyncio
from dtos.viewer_dto import FrameDTO
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

    async def end_session(self, session_id: str, dto: BaseWebSocketDTO):
        await self.get_session(session_id).put_frame(None)
        await super().end_session(session_id, dto)


class ViewerSession(WebsocketSession):
    def __init__(self, session_id: str, client: ViewerClient):
        super().__init__(session_id, client)
        self._frame: asyncio.Queue = asyncio.Queue()
        from tasks import viewer_task

        asyncio.create_task(
            viewer_task.run(self._client._client_id, building_id=session_id)
        )

    async def get_frame(self) -> str | None:
        return await self._frame.get()

    async def put_frame(self, frame):
        await self._frame.put(frame)


class ViewerManager(WebSocketManager):
    def __init__(self):
        super().__init__(ViewerClient, ViewerSession)
