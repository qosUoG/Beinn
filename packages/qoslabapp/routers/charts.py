import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from packages.qoslabapp.lib.state import AppState


router = APIRouter()


@router.websocket("/charts/{title}")
async def getChartDataWs(title: str, ws: WebSocket):
    await ws.accept()
    AppState.charts[title].connections.append(ws)

    if title not in AppState.charts:
        await ws.close()
        AppState.charts[title].connections.remove(ws)

    AppState.charts[title].has_listener.set()

    try:
        while True:
            await asyncio.sleep(1 / AppState.charts[title].rate)
            with AppState.charts[title]._lock():
                await asyncio.gather(
                    *[
                        con.send_json({"frames": AppState.charts[title].frames})
                        for con in AppState.charts[title].connections
                    ]
                )

                AppState.charts[title].frames.clear()

    except WebSocketDisconnect:
        if len(AppState.charts[title].connections) == 0:
            AppState.charts[title].has_listener.clear()


@router.get("/charts/{title}/config")
async def getChartConfig(title: str):
    if title not in AppState.charts:
        return json.dumps({"success": False})

    return AppState.charts[title].chart.getConfig()


class SetChartUpdateRatePayload:
    # hz
    rate: int


@router.post("/charts/{title}/rate")
async def setChartUpdateRate(title: str, rate: int):
    AppState.charts[title].rate = rate
