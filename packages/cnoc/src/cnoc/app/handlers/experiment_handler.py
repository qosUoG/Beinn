import asyncio
import json
from typing import Literal

from ..state.foundation import Foundation
from ..state.state import State
from ..utils.messenger import kv2str
from websockets import ServerConnection


async def experimentHandler(ws: ServerConnection, id: str):
    experiment = State.get(id)

    async def producer():
        
        experiment.onStarted(
            lambda: Foundation.runCoroThreadsafeBlocking(
                ws.send(kv2str("status", "started"))
            )
        )
        
        experiment.onLoopEnd(
            lambda iteration_count: Foundation.runCoroThreadsafeBlocking(
                ws.send(kv2str("iteration_count", iteration_count))
            )
        )
        
        experiment.onStopped(
            lambda
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
