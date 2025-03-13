"""Module initiates a websocket to send data at each frame."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypedDict, Unpack, override


@dataclass
class ChartABC(ABC):
    _initialize_fn: Callable[[], None]
    _plot_fn: Callable[[dict[str, float]], None]

    @abstractmethod
    def kwargs[T](self, **kwargs: T) -> T:
        # This method creates the kwargs object for instantiating the chart
        raise NotImplementedError

    @abstractmethod
    def plot(self, frame: Any) -> None:
        # This method plots a frame
        raise NotImplementedError

    @abstractmethod
    def getConfig(self) -> Any:
        # This function returns the config of the plot
        raise NotImplementedError


class ChartHolderABC(ABC):
    @classmethod
    @abstractmethod
    def createChart[T: ChartABC](cls, chartT: type[T], kwargs: Any) -> T:
        # This method returns a plot object
        raise NotImplementedError


@dataclass
class XYPlot(ChartABC):
    class Config(TypedDict):
        title: str
        x_name: str
        y_names: list[str]

    class KW(TypedDict):
        title: str
        x_name: str
        y_names: list[str]

    title: str
    x_name: str
    y_names: list[str]
    config: Config

    def __init__(
        self,
        plot_fn: Callable[[dict[str, float]], None],
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.x_name = kwargs["x_name"]
        self.y_names = kwargs["y_names"]
        self.config: XYPlot.Config = {
            "title": self.title,
            "x_name": self.x_name,
            "y_names": self.y_names,
        }
        self._plot_fn = plot_fn

    @override
    def kwargs(self, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def getConfig(self) -> Config:
        return self.config

    @override
    def plot(self, frame: dict[str, float]):
        self._plot_fn(frame)
