"""Mode of Scatter chart

append: append data in order

overwrite: overwrites the y value of the specified x value
"""

import array
from typing import Literal, override
from ._chart import ChartABC


type ScatterMode = Literal["append"] | Literal["overwrite"]


class Scatter(ChartABC):
    type = "chart:scatter"

    def __init__(
        self,
        title: str,
        mode: ScatterMode,
        x_axis: str,
        y_axis: str,
        y_names: list[str],
    ):
        self.title = title
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.y_names = y_names
        self.mode = mode

        super().__init__()

    @override
    def getConfig(self):
        return {
            "type": Scatter.type,
            "title": self.title,
            "x_axis": self.x_axis,
            "y_axis": self.y_axis,
            "y_names": self.y_names,
            "mode": self.mode,
        }

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
            # f64 byte array
            encoded = array.array("d")
            # 0: value of x
            encoded.append(frame["chart:x"])
            for y_name in self.y_names:
                if y_name in frame:
                    # If have value, takes two 8 byte floats.
                    # First 8 byte has 1 for indicating have value,
                    # Second 8 byte is the value itself
                    encoded.append(1)
                    encoded.append(frame[y_name])
                else:
                    # If without value, a 0 is put there
                    encoded.append(0)

            self._plot(bytes(encoded))
        except KeyError as e:
            raise Exception(f"key {e.args[0]} for frame of chart;scatter is wrong")
