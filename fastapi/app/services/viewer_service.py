from dtos.viewer_dto import (
    StartSessionRequestDTO,
    EndSessionRequestDTO,
    FrameDTO,
)
from dtos.base_dto import (
    BaseStartSessionDTO,
    BaseWebSocketDTO,
    BaseEndSessionDTO,
)
from managers import viewer_manager
from managers.viewer_manager import ViewerSession


async def start_session_request_service(
    client_id: str, dto: StartSessionRequestDTO
):
    if not viewer_manager.get_client(client_id).has_session(dto.session_id):
        await viewer_manager.get_client(client_id).start_session(
            dto.session_id,
            BaseWebSocketDTO[BaseStartSessionDTO](
                data=BaseStartSessionDTO(session_id=dto.session_id)
            ),
        )
        session: ViewerSession = viewer_manager.get_client(
            client_id
        ).get_session(dto.session_id)
        await session.init_internal_session(dto.session_id)
    else:
        await viewer_manager.get_client(client_id).send(
            BaseWebSocketDTO[BaseStartSessionDTO](
                data=BaseStartSessionDTO(session_id=dto.session_id)
            )
        )


async def end_session_request_service(
    client_id: str, dto: EndSessionRequestDTO
):
    await viewer_manager.get_client(client_id).end_session(
        dto.session_id,
        BaseWebSocketDTO[BaseEndSessionDTO](
            data=BaseEndSessionDTO(session_id=dto.session_id)
        ),
    )


async def frame_service(client_id: str, dto: FrameDTO):
    session: ViewerSession = viewer_manager.get_client(client_id).get_session(
        dto.session_id
    )
    await session.infer_frame(dto.frame)
