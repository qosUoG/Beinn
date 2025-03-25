import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..lib.settings.state import AppState


router = APIRouter()


@router.websocket("/chart/{experiment_id}/{title}")
async def getChartDataWs(experiment_id: str, title: str, ws: WebSocket):
    await ws.accept()

    (yieldFn, unsubscribe, setRate) = AppState.subscribeChart(experiment_id, title, ws)

    if yieldFn is None:
        await ws.close()
        return

    async def producer():
        try:
            while True:
                async for frames in yieldFn():
                    await ws.send_bytes(frames)
        except WebSocketDisconnect:
            unsubscribe()

    async def consumer():
        while True:
            data = await ws.receive_json()

            assert data["type"] == "rate"
            await setRate(data["value"])

    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())

    await producer_task
    consumer_task.cancel()
