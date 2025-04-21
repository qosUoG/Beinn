from contextlib import contextmanager, redirect_stderr
import sys
from threading import Lock
from typing import Iterator
from cnoc.equipment import EquipmentABC, EquipmentProxy as proto
from io import StringIO
from contextlib import redirect_stdout


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

    def cleanup(self):
        # wait for minimal time
        locked = self._lock.acquire(timeout=0.1)
        self._equipment.cleanup()
        if locked:
            self._lock.release()

    def interpret(self, code: str, name: str):
        code = code.replace(name, "equipment")
        with self.lock() as equipment:
            try:
                return {
                    "type": "eval",
                    "result": f"{eval(code, globals=globals(), locals=locals())}",
                }

            except SyntaxError:
                pass
            except Exception as e:
                return {
                    "type": "error",
                    "result": f"code: {code}, error:{e}",
                }

            try:
                f = StringIO()

                with redirect_stdout(f):
                    with redirect_stderr(sys.stdout):
                        exec(code, globals=globals(), locals=locals())

                return {
                    "type": "exec",
                    "result": f.getvalue(),
                }

            except Exception as e:
                return {
                    "type": "error",
                    "result": f"code: {code}, error:{e}",
                }
