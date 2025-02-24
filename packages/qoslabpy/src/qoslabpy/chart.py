"""
This module initiates a websocket to send data at each frame
"""

from websockets.sync.server import serve


class ChartWs:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        with serve(self.echo, self.address, self.port) as server:
            self.server = server
            server.serve_forever()

    def echo(self):
        """
        This is a write only socket.
        """
        pass

    def start(self):
        
