from typing import Dict

from .saver import Saver
from .charts._chart import ChartABC


class Manager:
    def __init__(self):
        self._savers: list[Saver] = []
        self._charts: Dict[str, ChartABC] = {}

        # Set the expected loop count, -1 means infinite
        self.expected_loop_count = -1

    def createChart(self, chart: ChartABC):
        self._charts[chart.title] = chart

    def createSaver(self, saver: Saver):
        self._savers.append(saver)

    @property
    def savers(self):
        return self._savers

    @property
    def charts(self):
        return self._charts
