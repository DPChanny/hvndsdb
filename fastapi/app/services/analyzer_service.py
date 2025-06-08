from dtos.analyzer_dto import (
    CancelDeblurGS,
    StartSessionRequestDTO,
    EndSessionRequestDTO,
)
from dtos.base_dto import (
    BaseStartSessionDTO,
    BaseWebSocketDTO,
    BaseEndSessionDTO,
)
from managers import analyzer_manager, deblur_gs_manager


async def start_session_request_service(
        client_id: str, dto: StartSessionRequestDTO
):
    if not analyzer_manager.has_analyzer_task(dto.session_id):
        analyzer_manager.start_analyzer_task(dto.session_id)
    if not analyzer_manager.get_client(client_id).has_session(dto.session_id):
        await analyzer_manager.get_client(client_id).start_session(
            dto.session_id,
            BaseWebSocketDTO[BaseStartSessionDTO](
                data=BaseStartSessionDTO(session_id=dto.session_id)
            ),
        )
    else:
        await analyzer_manager.get_client(client_id).send(
            BaseWebSocketDTO[BaseStartSessionDTO](
                data=BaseStartSessionDTO(session_id=dto.session_id)
            )
        )


async def end_session_request_service(
        client_id: str, dto: EndSessionRequestDTO
):
    await analyzer_manager.get_client(client_id).end_session(
        dto.session_id,
        BaseWebSocketDTO[BaseEndSessionDTO](
            data=BaseEndSessionDTO(session_id=dto.session_id)
        ),
    )


async def cancel_deblur_gs_service(dto: CancelDeblurGS):
    await deblur_gs_manager.cancel_session(dto.session_id)
