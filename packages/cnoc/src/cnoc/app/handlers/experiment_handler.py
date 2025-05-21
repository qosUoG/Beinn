import asyncio
import json
from typing import Literal

from ..state.foundation import Foundation
from ..state.state import State
from ..utils.messenger import kv2str
from websockets import ServerConnection


async def experimentHandler(ws: ServerConnection, id: str):
    experiment = State.get(id)

    if experiment is None:
        # Send error and close the connection
        await ws.send(kv2str("error", "experiment not found"))
        await ws.close()

    async def producer():
        # Experiment Life cycle status
        experiment.onStarted(
            lambda: Foundation.runCoroThreadsafeBlocking(
                ws.send(kv2str("status", "started"))
            )
        )
        experiment.onPaused(
            lambda: Foundation.runCoroThreadsafeBlocking(
                ws.send(kv2str("status", "paused"))
            )
        )
        experiment.onStopped(
            lambda success: Foundation.runCoroThreadsafeBlocking(
                ws.send(kv2str("status", "completed" if success else "stopped"))
            )
        )
        experiment.onLoopEnd(
            lambda iteration_count: Foundation.runCoroThreadsafeBlocking(
                ws.send(kv2str("iteration_count", iteration_count))
            )
        )

    async def consumer():
        async for message in ws:
            req = json.loads(message)
            action: Literal["start", "pause", "stop", "continue"] = req["action"]

            match action:
                case "start":
                    await experiment.start()
                    break
                case "pause":
                    experiment.pause()
                    break
                case "stop":
                    experiment.stop()
                    break
                case "continue":
                    experiment.unpause()
                    break

    consumer_task = asyncio.create_task(consumer())

    await producer()
    consumer_task.cancel()
