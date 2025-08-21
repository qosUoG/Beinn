import asyncio
import site
import sys
import time
from typing import Any
from urllib.parse import unquote

from .handlers.chart_handler import chartHandler

from .state.foundation import Foundation


# from .handlers.experiment_handler import experimentHandler
from .handlers.workspace_handler import workspaceHandler
from websockets import ServerConnection, serve

wss: list[ServerConnection] = []
task: asyncio.Task[Any] | None = None


async def handler(ws: ServerConnection):
    path = ws.request.path
    wss.append(ws)

    # Workspace
    if path == "/workspace":
        await workspaceHandler(ws)
        for _ws in wss:
            await _ws.close()

        assert task is not None
        task.cancel()
    elif path == "/close":
        for _ws in wss:
            await _ws.close()

        assert task is not None
        task.cancel()
    elif path.startswith("/chart"):
        await chartHandler(*unquote(path).split("/")[2:], ws)


async def _main():
    Foundation.setLoop(asyncio.get_running_loop())
    async with serve(handler, "localhost", 8001) as server:
        task = asyncio.create_task(server.serve_forever())
        await task


def main():
    roots: list[str]
    if "/" in __file__:
        roots = __file__.split("/")
    elif "\\" in __file__:
        roots = __file__.split("\\")
    venv_index = roots.index(".venv")
    path = "/".join(roots[:venv_index])

    site.addsitedir(path)
    asyncio.run(_main())


if __name__ == "__main__":
    main()
