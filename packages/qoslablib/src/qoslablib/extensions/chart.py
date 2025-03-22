"""Module initiates a websocket to send data at each frame."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import dataclasses

from typing import Any, Literal, TypedDict, Unpack, override


@dataclass
class ChartConfigABC(ABC):
    title: str
    type: str

    @abstractmethod
    def toDict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class ChartABC(ABC):
    _plot_fn: Callable[[dict[str, float]], None]
    config: ChartConfigABC

    @classmethod
    @abstractmethod
    def kwargs(self, **kwargs: Any) -> Any:
        # This method creates the kwargs object for instantiating the chart
        raise NotImplementedError

    @abstractmethod
    def plot(self, frame: Any) -> None:
        # This method plots a frame
        raise NotImplementedError


class ChartManagerABC(ABC):
    @classmethod
    @abstractmethod
    def createChart(cls, chartT: type[ChartABC], kwargs: Any) -> ChartABC:
        # This method returns a plot object
        raise NotImplementedError


@dataclass
class XYPlotConfig(ChartConfigABC):
    title: str
    type: Literal["XYPlot"]
    x_axis: str
    y_axis: str
    y_names: list[str]

    def toDict(self):
        return dataclasses.asdict(self)


@dataclass
class XYPlot(ChartABC):
    class KW(TypedDict):
        title: str
        x_axis: str
        y_axis: str
        y_names: list[str]

    title: str
    x_axis: str
    y_axis: str
    y_names: list[str]
    config: XYPlotConfig

    def __init__(
        self,
        plot_fn: Callable[[dict[str, float]], None],
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.x_axis = kwargs["x_axis"]
        self.y_names = kwargs["y_names"]
        self.config = XYPlotConfig(
            title=self.title,
            type="XYPlot",
            x_axis=self.x_axis,
            y_axis=self.y_axis,
            y_names=self.y_names,
        )

        self._plot_fn = plot_fn

    @classmethod
    @override
    def kwargs(self, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def plot(self, frame: dict[str, float]):
        self._plot_fn(frame)
