from typing import ClassVar

from dtos.base_dto import BaseSessionDataDTO


class StartSessionRequestDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "start_session_request"


class EndSessionRequestDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "end_session_request"


class FrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "frame"
    frame: str


class FrameCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "frame_complete"
