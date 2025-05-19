"""Charts to plot data in real time

Note that the data presented by the chart are not saved after the experiment.
To save data of experiment, please refer to the saver extension.

To see examples, refer to example/experiment directory.

    * XYConfig - Chart config of the XY line plot
    * XY - A xy line chart
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class ChartConfigABC(ABC):
    title: str
    _type: str
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
