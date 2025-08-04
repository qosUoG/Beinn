import asyncio
import json
from websockets import ConnectionClosed, ServerConnection

from ..state.experiments import Experiments


async def chartHandler(experiment_name: str, chart_name: str, ws: ServerConnection):
    # Subscribe websocket to chart stream
    (subscription, unsubscribe, setRate, getRate) = (
        Experiments.instances[experiment_name]
        .instance._cnoc_charts[chart_name]
        ._cnoc_subscribe(ws)
    )

    if subscription is None:
        await ws.close()
        return

    async def consumer():
        while True:
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
        print("ConnectionClosed", flush=True)
