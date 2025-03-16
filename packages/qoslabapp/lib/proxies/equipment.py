from threading import Lock

from typing import Any

from qoslablib.params import Params
from qoslablib.runtime import EquipmentABC


class EquipmentProxy:
    # Threading.Lock for thread safety access of Equipment

    def __init__(self, eCls: type[EquipmentABC]):
        super().__setattr__("_lock", Lock())
        super().__setattr__("_equipment", eCls())

    # For Type safety
    @property
    def params(self) -> Params:
        with super()._lock:
            return super()._equipment.params

    @params.setter
    def params(self, params: Params):
        with super()._lock:
            super()._equipment.params = params

    # Proxy to all underlying parameters
    def __getattr__(self, key: str):
        with super()._lock:
            attr = getattr(super()._equipment, key)
            if callable(attr):

                def wrap(*args, **kwargs):
                    with super()._lock:
                        return attr(*args, **kwargs)

                return wrap

            return attr

    def __setattr__(self, key: str, value: Any):
        with super()._lock:
            setattr(super()._equipment, key, value)
