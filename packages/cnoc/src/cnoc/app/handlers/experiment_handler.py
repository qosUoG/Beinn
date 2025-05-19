import asyncio
import json
from typing import Literal

from ..state.foundation import Foundation
from ..state.state import State
from ..utils.messenger import Messenger, kv2str
from websockets import ServerConnection


async def experimentHandler(ws: ServerConnection, id: str):
    messenger = Messenger(Foundation.getLoop())
    experiment = State.get(id)

    async def producer():
        # Messenger
        experiment.onStarted(
            lambda: Foundation.runCoroThreadsafeBlocking(
                ws.send(kv2str("status", "started"))
            )
        )

        pass

    async def consumer():
        async for message in ws:
            req = json.loads(message)
            action: Literal[""] = req["action"]

            match action:
                case "start":
                    pass
                case "pause":
                    pass
                case "stop":
                    pass
                case "continue":
                    pass

    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())

    await producer_task
    consumer_task.cancel()
