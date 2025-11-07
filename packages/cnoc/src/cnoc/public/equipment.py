"""Base Class of Equipment, and EquipmentProxy Protocol

For examples of defining equipment class (drivers), please refer to examples in
example/examplelib.

    * EquipmentABC - Base class of all equipment drivers
        Users shall define equipment drivers by using EquipmentABC as the base class.
    * EquipmentProxy - Threadsafe runtime wrapper of equipment drivers
        At runtime, equipment is wrapped by the EquipmentProxy.
        The class provides a contextmanager method which locks the underlying
        equipment instance while accessing. This means that code within the
        contextmanager is blocking.
"""

from abc import ABC, abstractmethod
from typing import Any, Never
from _typeshed import DataclassInstance


class EquipmentABC(ABC):
    """
    Base class of all equipment drivers

    Attributes
    ----------
    params : Params
        a dictionary of parameters accessible by the equipment driver

    """

    def setParams(
        self,
        params: dict[str, Any],
        equipments: dict[str, "EquipmentABC"],
        ParamsCls: type[DataclassInstance],
    ):
        from ._params import dict2Params

        self.params: DataclassInstance = dict2Params(params, equipments, ParamsCls)

    # def _cnoc_interpret(self, code: str, name: str):
    #     with self.lock:
    #         try:
    #             print(f"{eval(code, globals=globals(), locals=locals())}", flush=True)
    #             return

    #         except SyntaxError:
    #             pass
    #         except Exception as e:
    #             print(e, flush=True)
    #             return

    #         try:
    #             f = StringIO()

    #             with redirect_stdout(f):
    #                 with redirect_stderr(sys.stdout):
    #                     exec(code, globals=globals(), locals=locals())

    #         except Exception as e:
    #             print(e, flush=True)

    @abstractmethod
    def cleanup(self) -> Never:
        """
        Perform any clean up if needed

        This method would run when the workspace is closed. Users may perform
        any clean up in this method. Please be aware the equipment might be in any state
        when entering this function
        """
        raise NotImplementedError

    @abstractmethod
    def interactive(self) -> Never:
        """
        Code to run before REPL mode is entered
        """
        raise NotImplementedError
