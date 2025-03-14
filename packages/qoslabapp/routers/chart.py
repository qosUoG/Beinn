import asyncio
import json
from typing import Any, TypedDict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel


from ..lib.state import AppState


router = APIRouter()


@router.websocket("/chart/{experiment_id}/{title}")
async def getChartDataWs(experiment_id: str, title: str, ws: WebSocket):
    await ws.accept()

    if (
        experiment_id not in AppState.chart_handlers
        or title not in AppState.chart_handlers[experiment_id]
    ):
        await ws.close()

    AppState.chart_handlers[experiment_id][title].connections.append(ws)

    AppState.chart_handlers[experiment_id][title].has_listener.set()

    try:
        while True:
            await asyncio.sleep(1 / AppState.chart_handlers[experiment_id][title].rate)
            with AppState.chart_handlers[experiment_id][title]._lock:
                await asyncio.gather(
                    *[
                        con.send_json(
                            {
                                "frames": AppState.chart_handlers[experiment_id][
                                    title
                                ].frames
                            }
                        )
                        for con in AppState.chart_handlers[experiment_id][
                            title
                        ].connections
                    ]
                )

                AppState.chart_handlers[experiment_id][title].frames.clear()

    except WebSocketDisconnect:
        AppState.chart_handlers[experiment_id][title].connections.remove(ws)

        if len(AppState.chart_handlers[experiment_id][title].connections) == 0:
            AppState.chart_handlers[experiment_id][title].has_listener.clear()


class ChartConfigsByExperimentIdPayload(BaseModel):
    id: str


@router.post("/chart/configs")
async def getChartConfigByExperimentId(payload: ChartConfigsByExperimentIdPayload):
    class ReturnType(TypedDict):
        charts: dict[str, Any]

    res: ReturnType = {"charts": {}}

    if payload.id not in AppState.chart_handlers:
        return json.dumps({"charts": {}})

    for chart_handler in AppState.chart_handlers[payload.id].values():
        res["charts"][chart_handler.chart.config.title](chart_handler.chart.config)

    return res


class SetChartUpdateRatePayload(BaseModel):
    # hz
    rate: int


@router.post("/chart/{expeirment_id}/{title}/rate")
async def setChartUpdateRate(
    experiment_id: str, title: str, rate: SetChartUpdateRatePayload
):
    AppState.chart_handlers[experiment_id][title].rate = rate
