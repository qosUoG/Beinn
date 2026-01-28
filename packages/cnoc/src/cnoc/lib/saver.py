from typing import Mapping

from .manager import Manager
from ._saver import Saver as _S


class Saver[T: Mapping[str, object]]:
    def __init__(self, dir: str, title: str, schema: type[T], manager: Manager):
        self._saver = _S[T](dir, title, schema, manager)

    # Thread safe
    def save(self, data: T):
        self._saver.save(data)


# class Reader:
#     def __init__(self, path: str):
#         self.data = pd.read_parquet(path)  # type: ignore
#         self.time = int(pq.read_metadata(path).metadata[b"time"])  # type: ignore
#         self.params = json.loads(pq.read_metadata(path).metadata[b"params"])  # type: ignore
#         self.note = cast(str, pq.read_metadata(path).metadata[b"note"].decode())  # type: ignore
