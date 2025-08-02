import importlib
from typing import override

from ...public.equipment import EquipmentABC


from ._ees import EEInstance, EEsABC


class Equipments(EEsABC[EquipmentABC]):
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

        super().instances[name] = EEInstance[EquipmentABC](
            instance=getattr(module, cls_str)(),
            module=module_str,
            cls=cls_str,
        )

        return super().instances[name]
