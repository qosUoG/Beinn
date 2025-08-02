import importlib

from ...public.equipment import EquipmentABC


from .ees import EEInstance
from ...public.params import dict2Param


class Equipments:
    instances: dict[str, EEInstance[EquipmentABC]] = {}

    @classmethod
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

    @classmethod
    def save(cls, name: str, params: dict):
        cls.instances[name].instance.params = dict2Param(params)

    @classmethod
    def remove(cls, name: str):
        del cls.instances[name]
