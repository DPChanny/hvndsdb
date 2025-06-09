from .analyzer_manager import AnalyzerManager
from .deblur_gs_manager import DeblurGSManager
from .unity_manager import UnityManager
from .posenet_manager import PosenetManager
from .viewer_manager import ViewerManager

analyzer_manager: AnalyzerManager = AnalyzerManager()
deblur_gs_manager: DeblurGSManager = DeblurGSManager()
unity_manager: UnityManager = UnityManager()
posenet_manager: PosenetManager = PosenetManager()
viewer_manager: ViewerManager = ViewerManager()
