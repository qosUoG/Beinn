import asyncio

from .handlers.experiment_handler import experimentHandler
from .handlers.workspace_handler import workspaceHandler
from websockets import ServerConnection, serve


async def handler(ws: ServerConnection):
    if ws.request.path == "/":
        workspaceHandler(ws)
    elif ws.request.path.startswith("/experiment"):
        id = ws.request.path.split("/")[2]
        experimentHandler(ws, id)
    elif ws.request.path.startswith("/chart"):
        pass


async def main():
    async with serve(handler, "localhost", 8001) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
