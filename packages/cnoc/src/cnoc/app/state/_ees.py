from abc import ABC, abstractmethod
from dataclasses import dataclass

from ...public.params import dict2Param

from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC


@dataclass
class EEInstance[T: EquipmentABC | ExperimentABC]:
    instance: T
    module: str
    cls: str


class EEsABC[T: EquipmentABC | ExperimentABC](ABC):
    instances: dict[str, EEInstance[T]]

    @classmethod
    @abstractmethod
    def create(
        cls,
        name: str,
        module_str: str,
        cls_str: str,
    ):
        pass

    @classmethod
    def updateParams(cls, name: str, params: dict):
        cls.instances[name].instance.params = dict2Param(params)

    @classmethod
    def remove(cls, name: str):
        del cls.instances[name]
