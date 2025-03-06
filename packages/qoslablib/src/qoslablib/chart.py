"""
This module initiates a websocket to send data at each frame
"""

from collections.abc import Callable


class XYPlot:
    def __init__(
        self,
        *,
        title: str,
        x_name: str,
        y_names: list[str],
        plot_fn: Callable[[dict[str, float]], None],
    ):
        self.title = title
        self.x_name = x_name
        self.y_names = y_names
        self._plot_fn = plot_fn

    def plot(self, frame: dict[str, float]):
        self._plot_fn(frame)
