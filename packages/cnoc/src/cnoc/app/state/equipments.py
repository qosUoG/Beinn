import importlib

from ...public.params import _cnoc_dict2Params

from ...public.equipment import EquipmentABC


from ._ees import EEInstance


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
    def updateParams(cls, name: str, params: dict):
        cls.instances[name].instance.params = _cnoc_dict2Params(params)

        from .experiments import Experiments

        for experiment in Experiments.instances.values():
            for param in experiment.instance.params.values():
                if param._type == "equipment" and param.name == name:
                    experiment.instance._cnoc_saveParams()

    @classmethod
    def remove(cls, name: str):
        del cls.instances[name]
