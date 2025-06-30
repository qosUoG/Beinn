import asyncio


# from .handlers.experiment_handler import experimentHandler
from .handlers.workspace_handler import workspaceHandler
from websockets import ServerConnection, serve, Server

_server: Server | None = None


async def handler(ws: ServerConnection):
    path = ws.request.path

    # Workspace
    if path == "/":
        await workspaceHandler(ws)
    elif path == "/close":
        if _server is not None:
            await _server.close()

    # # Experiment
    # elif path.startswith("/experiment"):
    #     id = path.split("/")[2]
    #     experimentHandler(ws, id)

    # # Chart
    # elif path.startswith("/chart"):
    #     pass


async def _main():
    async with serve(handler, "localhost", 8001) as server:
        _server = server
        await server.serve_forever()


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
