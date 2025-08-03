import asyncio
import site
import sys

from .handlers.chart_handler import chartHandler

from .state.foundation import Foundation


# from .handlers.experiment_handler import experimentHandler
from .handlers.workspace_handler import workspaceHandler
from websockets import ServerConnection, serve


async def handler(ws: ServerConnection):
    path = ws.request.path

    # Workspace
    if path == "/workspace":
        await workspaceHandler(ws)
    elif path == "/close":
        await ws.close()
        sys.exit()
    elif path.startswith("/chart"):
        await chartHandler(*path.split("/")[2:], ws)


async def _main():
    Foundation.setLoop(asyncio.get_running_loop())
    async with serve(handler, "localhost", 8001) as server:
        await server.serve_forever()


def main():
    roots = __file__.split("/")
    venv_index = roots.index(".venv")
    path = "/".join(roots[:venv_index])

    site.addsitedir(path)
    asyncio.run(_main())


if __name__ == "__main__":
    main()
