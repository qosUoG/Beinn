from .experiment import ExperimentManagerABC
from .extensions.saver import SaverManagerABC
from .extensions.chart import ChartManagerABC


class ManagerABC(SaverManagerABC, ChartManagerABC, ExperimentManagerABC):
    pass
