from typing import Generic, Optional, TypeVar, ClassVar

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel


class BaseDataDTO(BaseModel):
    def get_type(self) -> Optional[str]:
        return getattr(self.__class__, "type", None)


T = TypeVar("T", bound=BaseDataDTO)


class BaseWebSocketDTO(GenericModel, Generic[T]):
    data: Optional[T] = None
    type: str = ""

    @validator("type", always=True, pre=True)
    def set_type_from_data(cls, v, values):
        data = values.get("data")
        if v:
            return v
        if data and hasattr(data, "get_type"):
            return data.get_type()
        return ""


class BaseSessionDataDTO(BaseDataDTO):
    session_id: str


class BaseStartSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "start_session"


class BaseSessionReadyDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "session_ready"


class BaseEndSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "end_session"


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


class UploadDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload"
    posenet_url: str


class UploadCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload_complete"


class ProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "progress"
    progress: str


class CompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "complete"
