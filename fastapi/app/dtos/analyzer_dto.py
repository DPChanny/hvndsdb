from typing import ClassVar

from dtos.base_dto import BaseSessionDataDTO


class CancelDeblurGS(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_deblur_gs"


class CancelPosenet(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_posenet"


class StartSessionRequestDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "start_session_request"


class EndSessionRequestDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "end_session_request"


class CenterFrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "center_frame"
    frame: str


class AroundFrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "around_frame"
    frame: str


class PosenetProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "posenet_progress"
    progress: str


class DeblurGSProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "deblur_gs_progress"
    progress: str


class ProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "progress"
    progress: str
