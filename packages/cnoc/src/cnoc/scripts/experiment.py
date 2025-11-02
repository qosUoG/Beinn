import asyncio
from urllib.parse import unquote
import json
from typing import Any, TypedDict
from websockets import ConnectionClosed, ServerConnection


from ._experiment import App
from .utils import preloadLocal
from websockets.asyncio.server import serve


class Globals:
    task: asyncio.Task
    app: App
    wss: list[ServerConnection] = []


class InstancePayload(TypedDict):
    name: str
    module: str
    cls: str
    params: dict[str, Any]


class StartPayload(TypedDict):
    equipments: list[InstancePayload]
    experiment: InstancePayload


async def chartHandler(chart_name: str, ws: ServerConnection):
    # Subscribe websocket to chart stream
    chart = Globals.app._manager._charts[chart_name]

    try:
        async for frames in chart.subscribe():
            if frames:
                print("frames", frames, flush=True)
                await ws.send(frames)

    except ConnectionClosed:
        chart.stop()
        print("stopped", flush=True)

    await ws.close(4000)
    print("ended", flush=True)


async def experimentHandler(ws: ServerConnection):
    try:
        async for message in ws:
            res = json.loads(message)
            match res["event"]:
                case "start":
                    Globals.app = App(ws, asyncio.get_running_loop(), res["value"])
                    await Globals.app.start()
                case "pause":
                    Globals.app.pause()
                case "stop":
                    Globals.app.stop()
                case "continue":
                    Globals.app.cont()
                case "save_note":
                    Globals.app.saveNote(res["value"])
                case "interpret":
                    if "name" in res["value"]:
                        Globals.app.interpret(
                            res["value"]["command"], res["value"]["name"]
                        )
                    else:
                        Globals.app.interpret(res["value"]["command"])
    except ConnectionClosed:
        Globals.app.kill()
        for ws in Globals.wss:
            await ws.close(4000)
        Globals.task.cancel()


async def handler(ws: ServerConnection):
    path = ws.request.path

    Globals.wss.append(ws)

    # Workspace
    if path == "/experiment":
        await experimentHandler(ws)

    elif path.startswith("/chart"):
        # unquote.split => ["", "chart", "<chart_title>"]
        print("connect", flush=True)
        print(Globals.wss[0].state, flush=True)
        await chartHandler(unquote(path).split("/")[2], ws)

    elif path == "/close":
        Globals.app.kill()
        for ws in Globals.wss:
            await ws.close()
        Globals.task.cancel()


async def _main():
    preloadLocal()
    async with serve(handler, "localhost", 8080) as server:
        Globals.task = asyncio.create_task(server.serve_forever())
        # This asks beinn to connect to the websocket server
        print("ws:loaded", flush=True)
        try:
            await Globals.task
        except asyncio.CancelledError:
            return


def main():
    asyncio.run(_main())
