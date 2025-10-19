from typing import Dict

from .saver import Saver
from .charts._chart import ChartABC


class Manager:
    def __init__(self):
        self._savers: list[Saver] = []
        self._charts: Dict[str, ChartABC] = {}
        self._expected_loop_count = -1

    def createChart(self, chart: ChartABC):
        self._charts[chart.title] = chart

    def createSaver(self, saver: Saver):
        self._savers.append(saver)

    @property
    def expected_loop_count(self):
        return self._expected_loop_count

    @expected_loop_count.setter
    def expected_loop_count(self, loop_count: int):
        self._expected_loop_count = loop_count

    def chartConfigs(self):
        return {k: v.getConfig() for k, v in self._charts.items()}

    def saverConfigs(self):
        return [s.path for s in self._savers]

    def close(self):
        for chart in self._charts.values():
            chart.close()
        for saver in self._savers:
            saver.close()
