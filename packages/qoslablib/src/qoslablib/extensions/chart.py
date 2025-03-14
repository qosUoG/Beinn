"""Module initiates a websocket to send data at each frame."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import dataclasses
import json
from typing import Any, Literal, TypedDict, Unpack, override


@dataclass
class ChartConfigABC[T: str](ABC):
    title: str
    type: T

    @abstractmethod
    def toJson(self) -> str:
        raise NotImplementedError


@dataclass
class ChartABC[T: ChartConfigABC](ABC):
    _initialize_fn: Callable[[], None]
    _plot_fn: Callable[[dict[str, float]], None]
    config: T

    def initialize(self) -> None:
        self._initialize_fn()

    @classmethod
    @abstractmethod
    def kwargs[T](self, **kwargs: T) -> T:
        # This method creates the kwargs object for instantiating the chart
        raise NotImplementedError

    @abstractmethod
    def plot(self, frame: Any) -> None:
        # This method plots a frame
        raise NotImplementedError


class ChartHolderABC(ABC):
    @classmethod
    @abstractmethod
    def createChart[T: ChartABC](cls, chartT: type[T], kwargs: Any) -> T:
        # This method returns a plot object
        raise NotImplementedError


@dataclass
class XYPlotConfig(ChartConfigABC[Literal["XYPlot"]]):
    title: str
    type: Literal["XYPlot"]
    x_name: str
    y_names: list[str]

    def toJson(self) -> str:
        return json.dumps(dataclasses.asdict(self))


@dataclass
class XYPlot(ChartABC[XYPlotConfig]):
    class KW(TypedDict):
        title: str
        x_name: str
        y_names: list[str]

    title: str
    x_name: str
    y_names: list[str]
    config: XYPlotConfig

    def __init__(
        self,
        initialize_fn: Callable[[], None],
        plot_fn: Callable[[dict[str, float]], None],
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.x_name = kwargs["x_name"]
        self.y_names = kwargs["y_names"]
        self.config = XYPlotConfig(
            title=self.title,
            type="XYPlot",
            x_name=self.x_name,
            y_names=self.y_names,
        )
        self._initialize_fn = initialize_fn
        self._plot_fn = plot_fn

    @classmethod
    @override
    def kwargs(self, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def plot(self, frame: dict[str, float]):
        self._plot_fn(frame)
