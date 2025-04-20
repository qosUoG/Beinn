from contextlib import contextmanager
from threading import Lock
from typing import Iterator
from cnoc.equipment import EquipmentABC, EquipmentProxy as proto


class EquipmentProxy[T: EquipmentABC](proto):
    def __init__(self, eCls: type[T]):
        self._lock = Lock()
        self._equipment = eCls()

    @property
    def params(self):
        return self._equipment.params

    @contextmanager
    def lock(self) -> Iterator[T]:
        try:
            with self._lock:
                yield self._equipment
        finally:
            pass
