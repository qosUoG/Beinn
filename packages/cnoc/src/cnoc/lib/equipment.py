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
from typing import Any, cast
from ._utils import DataclassInstance


class EquipmentABC[T: DataclassInstance](ABC):
    """
    Base class of all equipment drivers

    Attributes
    ----------
    params : Params
        a dictionary of parameters accessible by the equipment driver

    """

    def __init__(self):
        self.params: T

    def setParams(
        self,
        params: dict[str, Any],
        equipments: dict[str, "EquipmentABC[Any]"],
        ParamsCls: type[DataclassInstance],
    ):
        from ._params import dict2Params

        self.params = cast(T, dict2Params(params, equipments, ParamsCls))

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
    def cleanup(self) -> None:
        """
        Perform any clean up if needed

        This method would run when the workspace is closed. Users may perform
        any clean up in this method. Please be aware the equipment might be in any state
        when entering this function
        """
        raise NotImplementedError

    @abstractmethod
    def initialize(self) -> None:
        """
        Code to run before  the equipment is actually usable.
        Params are loaded before running this function.
        """
        raise NotImplementedError

    @abstractmethod
    def interactive(self) -> None:
        """
        Code to run before REPL mode is entered
        """
        raise NotImplementedError

    @abstractmethod
    def snapshot(self) -> Any:
        """
        Take a snapshot of equipment status and return as a dict.
        Use in conjunction with saver.saveMetadata
        """
        raise NotImplementedError
