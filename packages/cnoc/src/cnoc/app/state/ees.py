from dataclasses import dataclass

from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC


@dataclass
class EEInstance[T: EquipmentABC | ExperimentABC]:
    instance: T
    module: str
    cls: str
