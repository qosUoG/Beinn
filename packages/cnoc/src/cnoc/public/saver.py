import time
from typing import Any, Mapping, TypedDict
from ._saver import Saver as _S
from ._utils import DataclassInstance


class Metadata(TypedDict):
    time: time.struct_time
    params: dict[str, Any]
    note: str


class Saver[T: Mapping[str, object]]:
    def __init__(self, path: str, params: DataclassInstance, type: type[T]):
        self._saver = _S[T](path, params, type)

    def save(self, data: T):
        self._saver.save(data)

    @property
    def saver(self):
        return self._saver
