import importlib
from typing import override

from ...public.params import dict2Param

from ...public.equipment import EquipmentABC


from ._ees import EEInstance


class Equipments:
    instances: dict[str, EEInstance[EquipmentABC]] = {}

    @classmethod
    @override
    def create(
        cls,
        name: str,
        module_str: str,
        cls_str: str,
    ):
        module = importlib.import_module(module_str)
        module = importlib.reload(module)

        cls.instances[name] = EEInstance[EquipmentABC](
            instance=getattr(module, cls_str)(),
            module=module_str,
            cls=cls_str,
        )

        return cls.instances[name]

    def updateParams(cls, name: str, params: dict):
        cls.instances[name].instance.params = dict2Param(params)

    def remove(cls, name: str):
        del cls.instances[name]
