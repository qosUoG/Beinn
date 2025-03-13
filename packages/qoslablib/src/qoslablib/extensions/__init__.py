from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Unpack


@dataclass
class ExtentionABC(ABC):
    def initialize(self) -> None:
        # This function is not a must to be implemented
        pass

    @abstractmethod
    def kwargs[KW](self, **kwargs: Unpack[KW]) -> KW:
        # This method creates the kwargs object for instantiating the extension
        raise NotImplementedError

    @abstractmethod
    def plot(self, frame) -> None:
        # This method plots a frame
        raise NotImplementedError

    @abstractmethod
    def getConfig(self) -> dict[str, Any]:
        # This function returns the config of the extension
        raise NotImplementedError
