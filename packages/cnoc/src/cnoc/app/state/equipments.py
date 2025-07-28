import importlib
from ..proxies.equipment import EquipmentABC, EquipmentProxy


class Equipments:
    _proxies: dict[str, EquipmentProxy[EquipmentABC]] = {}

    @classmethod
    def create(
        cls,
        name: str,
        module_str: str,
        cls_str: str,
    ):
        module = importlib.import_module(module_str)
        module = importlib.reload(module)

        cls._proxies[name] = EquipmentProxy(
            getattr(module, cls_str), module_str, cls_str, name
        )

        return cls._proxies[name].js
