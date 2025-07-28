from contextlib import contextmanager, redirect_stderr, redirect_stdout
import sys
from threading import Lock
from typing import Iterator

from ...public.params import param2Dict
from ...public.equipment import EquipmentABC
from io import StringIO


class EquipmentProxy[T: EquipmentABC](T):
    def __init__(self, eCls: type[T], module: str, cls: str, name: str):
        self._lock = Lock()
        self._equipment = eCls()
        self.module = module
        self.cls = cls
        self.name = name

    @property
    def params(self):
        return self._equipment.params

    @property
    def js(self):
        return {
            "name": self.name,
            "module": self.module,
            "cls": self.cls,
            "params": param2Dict(self.params),
        }

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
