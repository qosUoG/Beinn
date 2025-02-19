from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from multiprocessing import Process, shared_memory
from multiprocessing.synchronize import Event

import numpy as np
from websockets.sync.client import connect
from .params import AllParamTypes


class ExperimentABC(ABC):
    params: dict[str, AllParamTypes]

    @classmethod
    @abstractmethod
    def initialize(cls):
        """
        Override to initialize the equipment.
        Do checks and resets in this function
        """
        ...

    @classmethod
    @abstractmethod
    def loop(cls):
        """
        Procedures to be ran in each loop
        """
        ...


class QosLab:
    address: str = "localhost:4000"

    @classmethod
    def config(cls, *, address: str | None = None):
        if address is not None:
            cls.address = address

        return QosLab

    @classmethod
    def set_experiment(cls, experiment: type[ExperimentABC]):
        cls.experiment = experiment

        return QosLab

    @classmethod
    def _start(cls, e: Event, *args, **kargs):
        cls.experiment(kargs)

    @classmethod
    def start(cls) -> None:
        with connect(f"ws://{cls.address}") as ws:
            # Once established connection, send the param descriptor of the experiment to the frontend
            ws.send(
                json.dumps(
                    {
                        "command": "EXPERIMENT-PARAMS",
                        "payload": json.dump(cls.experiment.params),
                    }
                )
            )
            for message in ws:
                decoded = json.loads(message)
                match decoded.command:
                    case "PLAY":
                        p = Process(target=cls._start)
                        pass
                    case "PAUSE":
                        # Phase2
                        pass
                    case "STOP":
                        # TODO
                        pass


@dataclass
class ChartConfig:
    h_axis_name: str
    v_axis_name: str


class Memory:
    def __init__(self, size: int, dtype: np.dtype):
        self.shm = shared_memory.SharedMemory(create=True, size=size)
        self.arr = np.ndarray(1, dtype=dtype, buffer=self.shm.buf)

    @classmethod
    def range(cls, start: int, stop: int, step: int, dtype: np.dtype):
        return Memory((stop - start) / step + 1, dtype)


if __name__ == "__main__":
    QosLab.config().start()
