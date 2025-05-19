"""Mode of XY chart

append: append data in order

overwrite: overwrites the y value of the specified x value
"""

import array
from dataclasses import dataclass
import dataclasses
from typing import Literal, TypedDict, Unpack, override

from cnoc.extensions.chart import ChartABC, ChartConfigABC
from cnoc.public.managers import ChartManagerABC


type XYMode = Literal["append"] | Literal["overwrite"]


@dataclass
class XYConfig(ChartConfigABC):
    """
    Config of XY line chart

    Attributes
    ----------
    title : str
        title of the chart
    mode : XYMode
        mode of the chart
    x_axis : str
        label of x axis
    y_axis : str
        label of y axis
    y_names : list[str]
        names of the list of data
    """

    title: str
    _type: Literal["chart:xy"]
    mode: XYMode
    x_axis: str
    y_axis: str
    y_names: list[str]

    def toDict(self):
        return dataclasses.asdict(self)


class XY(ChartABC):
    class KW(TypedDict):
        title: str
        mode: XYMode
        x_axis: str
        y_axis: str
        y_names: list[str]

    def __init__(
        self,
        *,
        manager: ChartManagerABC,
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.x_axis = kwargs["x_axis"]
        self.y_axis = kwargs["y_axis"]
        self.y_names = kwargs["y_names"]
        self.mode = kwargs["mode"]
        self.config = XYConfig(
            title=self.title,
            _type="chart:xy",
            x_axis=self.x_axis,
            y_axis=self.y_axis,
            y_names=self.y_names,
            mode=self.mode,
        )

        self._plot_fn = manager.registerChart(self)

    @override
    def plot(self, frame: dict[str, float]):
        """
        Plots a data point

        Parameters
        ----------
        frame: dict[str, float]
            chart:x : value of x MUST BE PRESENT
            <y_name> : <value> value of y, MUST have at least one
        """
        try:
            real_frame = array.array("d")
            # 0: value of x
            real_frame.append(frame["chart:x"])
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
