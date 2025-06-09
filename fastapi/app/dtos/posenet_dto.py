from typing import Optional, ClassVar

from dtos.base_dto import (
    BaseStartSessionDTO,
    BaseSessionDataDTO,
)


class StartSessionDTO(BaseStartSessionDTO):
    frames_url: str
    colmap_url: str
    posenet_url: Optional[str] = None


class StartTrainDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "start_train"


class CancelSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_session"


class CancelSessionCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_session_complete"


class UploadDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload"
    posenet_url: str


class UploadCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload_complete"


class ProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "progress"
    progress: str


class FrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "frame"
    frame: str


class SixDOFDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "6dof"
    px: float
    py: float
    pz: float
    rx: float
    ry: float
    rz: float
    rw: float


class CompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "complete"
