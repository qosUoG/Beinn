"""Module initiates a websocket to send data at each frame."""

from abc import ABC, abstractmethod
import array
from collections.abc import Callable
from dataclasses import dataclass
import dataclasses

from typing import Any, Literal, TypedDict, Unpack, override


@dataclass
class ChartConfigABC(ABC):
    title: str
    type: str
    mode: str

    @abstractmethod
    def toDict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class ChartABC(ABC):
    _plot_fn: Callable[[bytes], None]
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


type XYPlotMode = Literal["append"] | Literal["overwrite"]


@dataclass
class XYPlotConfig(ChartConfigABC):
    title: str
    type: Literal["XYPlot"]
    mode: XYPlotMode
    x_axis: str
    y_axis: str
    y_names: list[str]

    def toDict(self):
        return dataclasses.asdict(self)


class XYPlot(ChartABC):
    class KW(TypedDict):
        title: str
        mode: XYPlotMode
        x_axis: str
        y_axis: str
        y_names: list[str]

    def __init__(
        self,
        plot_fn: Callable[[bytes], None],
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.x_axis = kwargs["x_axis"]
        self.y_axis = kwargs["y_axis"]
        self.y_names = kwargs["y_names"]
        self.mode = kwargs["mode"]
        self.config = XYPlotConfig(
            title=self.title,
            type="XYPlot",
            x_axis=self.x_axis,
            y_axis=self.y_axis,
            y_names=self.y_names,
            mode=self.mode,
        )

        self._plot_fn = plot_fn

    @classmethod
    @override
    def kwargs(self, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def plot(self, frame: dict[str, float]):
        # there should always be an x value
        try:
            real_frame = array.array("d")
            # 0: value of x
            real_frame.append(frame["x"])
            for y_name in self.y_names:
                if y_name in frame:
                    # If have value, takes two 8 byte floats.
                    # First 8 byte has 1 for indicating have value,
                    # Second 8 byte is the value itself
                    real_frame.append(1)
                    real_frame.append(frame[y_name])
                else:
                    # If without value, a 0 is put there
                    real_frame.append(0)

            self._plot_fn(real_frame.tobytes())
        except KeyError as e:
            raise Exception(f"key {e.args[0]} for xyplot frame is wrong")
