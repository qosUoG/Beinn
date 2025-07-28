import asyncio
import sys


# from .handlers.experiment_handler import experimentHandler
from .handlers.workspace_handler import workspaceHandler
from websockets import ServerConnection, serve


async def handler(ws: ServerConnection):
    path = ws.request.path

    print(f"path: {path}", flush=True)

    # Workspace
    if path == "/workspace":
        await workspaceHandler(ws)
    elif path == "/close":
        sys.exit()

    # # Experiment
    # elif path.startswith("/experiment"):
    #     id = path.split("/")[2]
    #     experimentHandler(ws, id)

    # # Chart
    # elif path.startswith("/chart"):
    #     pass


async def _main():
    async with serve(handler, "localhost", 8001) as server:
        await server.serve_forever()


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
