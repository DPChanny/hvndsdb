import asyncio

from dtos.analyzer_dto import (
    AroundFrameDTO,
    CenterFrameDTO,
    ProgressDTO,
    PosenetProgressDTO,
    DeblurGSProgressDTO,
)
from dtos.base_dto import BaseWebSocketDTO, BaseEndSessionDTO
from managers.web_socket_manager import (
    WebSocketManager,
    WebsocketSession,
    WebsocketClient,
)
from tasks import analyzer_task


class AnalyzerClient(WebsocketClient):
    async def update_progress(self, building_id: str, progress: str):
        await self.send(
            BaseWebSocketDTO[ProgressDTO](
                data=ProgressDTO(progress=progress, session_id=building_id)
            )
        )

    async def update_posenet_progress(self, building_id: str, progress: str):
        await self.send(
            BaseWebSocketDTO[PosenetProgressDTO](
                data=PosenetProgressDTO(
                    progress=progress, session_id=building_id
                )
            )
        )

    async def update_deblur_gs_progress(self, building_id: str, progress: str):
        await self.send(
            BaseWebSocketDTO[DeblurGSProgressDTO](
                data=DeblurGSProgressDTO(
                    progress=progress, session_id=building_id
                )
            )
        )

    async def update_center_frame(self, building_id: str, frame: str):
        await self.send(
            BaseWebSocketDTO[CenterFrameDTO](
                data=CenterFrameDTO(frame=frame, session_id=building_id)
            )
        )

    async def update_around_frame(self, building_id: str, frame: str):
        await self.send(
            BaseWebSocketDTO[AroundFrameDTO](
                data=AroundFrameDTO(frame=frame, session_id=building_id)
            )
        )


class AnalyzerSession(WebsocketSession):
    def __init__(self, session_id: str, client: AnalyzerClient):
        super().__init__(session_id, client)
        self.set_ready()


class AnalyzerManager(WebSocketManager):
    def __init__(self):
        super().__init__(AnalyzerClient, AnalyzerSession)
        self._analyzer_tasks: dict[str, asyncio.Task] = {}

    async def _handle_task_done(self, building_id: str):
        self._analyzer_tasks.pop(building_id)

        for client in self._clients.values():
            if client.has_session(building_id):
                await client.end_session(
                    building_id,
                    BaseWebSocketDTO[BaseEndSessionDTO](
                        data=BaseEndSessionDTO(session_id=building_id)
                    ),
                )

    def start_analyzer_task(self, building_id: str):
        if building_id in self._analyzer_tasks:
            raise LookupError(f"Analyzer task {building_id} already exists")

        task = asyncio.create_task(analyzer_task.run(building_id))
        self._analyzer_tasks[building_id] = task

        task.add_done_callback(
            lambda t: asyncio.create_task(self._handle_task_done(building_id))
        )

    def has_analyzer_task(self, building_id: str) -> bool:
        return building_id in self._analyzer_tasks

    def get_analyzer_task(self, building_id: str) -> asyncio.Task:
        analyzer = self._analyzer_tasks.get(building_id)
        if not analyzer:
            raise LookupError(f"No analyzer task found {building_id}")

        return analyzer

    async def update_progress(self, building_id: str, progress: str):
        for client in list(self._clients.values()):
            if client.has_session(building_id):
                await client.update_progress(building_id, progress)

    async def update_deblur_gs_progress(self, building_id: str, progress: str):
        for client in list(self._clients.values()):
            if client.has_session(building_id):
                await client.update_deblur_gs_progress(building_id, progress)

    async def update_posenet_progress(self, building_id: str, progress: str):
        for client in list(self._clients.values()):
            if client.has_session(building_id):
                await client.update_posenet_progress(building_id, progress)

    async def update_center_frame(self, building_id: str, frame: str):
        for client in list(self._clients.values()):
            if client.has_session(building_id):
                await client.update_center_frame(building_id, frame)

    async def update_around_frame(self, building_id: str, frame: str):
        for client in list(self._clients.values()):
            if client.has_session(building_id):
                await client.update_around_frame(building_id, frame)
