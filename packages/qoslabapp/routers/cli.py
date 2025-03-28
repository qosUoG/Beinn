from fastapi import APIRouter, WebSocket

from ..lib.settings.state import AppState


router = APIRouter()


@router.websocket("/cli")
async def cli(ws: WebSocket):
    # This websocket shall keep accepting commands and post back result of the commands
    await ws.accept()

    while True:
        data = await ws.receive_json()
        if data["type"] == "equipment":
            await ws.send_text(f"{AppState.equipmentCli(data['id'], data['command'])}")
        else:
            await ws.send_text(f"{eval(data['command'])}")
