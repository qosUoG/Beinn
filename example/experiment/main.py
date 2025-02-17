import asyncio
from websockets import ServerConnection
from websockets.asyncio.server import serve


class ExampleExperiment:
    @classmethod
    def initialize():
        # setup chart socket
        pass
        # setup sqlite dta logging

    @classmethod
    def main():
        pass


async def onmessage(websocket: ServerConnection):
    async for message in websocket:
        print(message)
        await websocket.send(message)


async def server_socket():
    async with serve(onmessage, "localhost", 8765) as server:
        print("python websocket established")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(server_socket())
