"""
This module initiates a websocket to send data at each frame
"""

import json
from multiprocessing.synchronize import Lock as LockT, Event as EventT
from websockets import ConnectionClosed, ServerConnection

from websockets.sync.server import serve
from multiprocessing import Manager, Process, Event


class ChartWsMp:
    def __init__[T](self, address: str, port: int, framedata: T, lock: LockT):
        self.address = address
        self.port = port
        self.manager = Manager()
        self.framedata = self.manager.dict(framedata)
        self.lock = lock
        self._event = Event()

    def start(self):
        self.mp = Process(
            target=ChartWsMp._serve,
            args=(self.address, self.port, self.framedata, self.lock, self._event),
        )

    def _serve[T](address: str, port: int, framedata: T, lock: LockT, event: EventT):
        chart = ChartWs(address, port, framedata, lock, event)
        chart.start()

    def plot[T](self, framedata: T):
        self.framedata = framedata
        self._event.set()


class ChartWs:
    def __init__[T](
        self,
        address: str,
        port: int,
        framedata: T,
        lock: LockT,
        event: EventT = Event(),
    ):
        self.address = address
        self.port = port
        self.lock = lock
        self._event = event
        self.framedata = framedata

    def start(self):
        with serve(self._send, self.address, self.port) as server:
            self.server = server
            server.serve_forever()

    def plot[T](self, framedata: T):
        self.framedata = framedata
        self._event.set()

    def _send(self, websocket: ServerConnection):
        """
        This is a write only socket.
        """
        while True:
            try:
                self._event.wait()
                self.lock.acquire()
                if self.framedata:
                    websocket.send(json.dumps(self.framedata))
                    self.framedata.clear()
                self.lock.release()
            except ConnectionClosed:
                break
