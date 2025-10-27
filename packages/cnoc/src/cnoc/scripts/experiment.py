import asyncio
from urllib.parse import unquote
import json
from typing import Any, TypedDict
from websockets import ConnectionClosed, ServerConnection


from ._experiment import App
from .utils import preloadLocal
from websockets.asyncio.server import serve


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
    (subscription, unsubscribe, setRate, getRate) = App.manager._charts[
        chart_name
    ].subscribe(ws)

    if subscription is None:
        await ws.close()
        return

    async def consumer():
        async for message in ws:
            data = json.loads(message)
            assert data["command"] == "rate"
            await setRate(data["value"])
            await ws.send(json.dumps({"command": "rate", "value": getRate()}))

    consumer_task = asyncio.create_task(consumer())

    try:
        async for frames in subscription():
            if frames:
                await ws.send(frames)

        consumer_task.cancel()
        unsubscribe()
        await ws.close(4000)
        return

    except ConnectionClosed:
        consumer_task.cancel()
        unsubscribe()


async def experimentHandler(ws: ServerConnection):
    # print("ws:loaded", flush=True)
    try:
        async for message in ws:
            res = json.loads(message)
            match res["event"]:
                case "start":
                    await App.start(res["value"], ws)
                case "pause":
                    App.state.pause()
                case "stop":
                    App.state.stop()
                case "continue":
                    App.state.cont()
                case "save_note":
                    App.saveNote(res["value"])
                case "interpret":
                    if "name" in res["value"]:
                        App.interpret(res["value"]["command"], res["value"]["name"])
                    else:
                        App.interpret(res["value"]["command"])
    except ConnectionClosed:
        App.state.stop()
        App.task.cancel()


async def handler(ws: ServerConnection):
    path = ws.request.path

    # Workspace
    if path == "/experiment":
        await experimentHandler(ws)

    elif path.startswith("/chart"):
        # unquote.split => ["", "chart", "<chart_title>"]
        await chartHandler(unquote(path).split("/")[2], ws)

    elif path == "/close":
        await ws.close()
        App.task.cancel()


async def _main():
    preloadLocal()
    async with serve(handler, "localhost", 8080) as server:
        App.task = asyncio.create_task(server.serve_forever())
        print("ws:loaded", flush=True)
        try:
            await App.task
        except asyncio.CancelledError:
            pass


def main():
    asyncio.run(_main())
