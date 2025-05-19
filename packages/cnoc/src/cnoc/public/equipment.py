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
from contextlib import contextmanager
from typing import Iterator, Protocol


class EquipmentABC(ABC):
    """
    Base class of all equipment drivers

    Attributes
    ----------
    params : .params.Params
        a dictionary of parameters accessible by the equipment driver

    """

    def __init__(self):
        """
        No parameters shall be passed to the __init__ function.

        Implementation of drivers shall also make sure to instantiate the
        self.params attribute as well.

        To be type safe, implementors may also define a params type specific
        to the equipment driver. Detail please refer to example/examplelib
        """
        from .params import Params

        self.params: Params

    def cleanup(self):
        """
        Perform any clean up if needed

        This method would run when the workspace is closed. Users may perform
        any clean up in this method. Please be aware the equipment might be in any state
        when entering this function

        It is optional to implement this method.
        """
        pass


class EquipmentProxy[T: EquipmentABC](Protocol):
    """
    Wrapper class of equipment driver during runtime

    Methods
    ----------
    lock()
        A contextmanager for threadsafe access of the underlying equipment.
        Users would need to attain the lock to access the equipment instance.
    """

    @contextmanager
    @abstractmethod
    def lock(self) -> Iterator[T]:
        raise NotImplementedError
