from dtos.base_dto import BaseSessionReadyDTO
from dtos.unity_dto import FrameDTO
from managers import unity_manager
from managers.unity_manager import UnitySession


def session_ready_service(client_id: str, dto: BaseSessionReadyDTO):
    unity_manager.get_client(client_id).get_session(dto.session_id).set_ready()


async def frame_service(client_id: str, dto: FrameDTO):
    try:
        session: UnitySession = unity_manager.get_client(client_id).get_session(
            dto.session_id
        )
        await session.put_frame(dto.frame)
    except LookupError:
        pass
