from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..lib.settings.state import AppState


router = APIRouter()


@router.websocket("/cli")
async def cli(ws: WebSocket):
    # This websocket shall keep accepting commands and post back result of the commands
    await ws.accept()
    try:
        while True:
            try:
                data = await ws.receive_json()
            except Exception as e:
                print(e, flush=True)

            if data["type"] == "equipment":
                code = f"AppState._equipment_proxies['{data['id']}']{data['command']}"
                await ws.send_json(AppState.interpret(code))
            else:
                await ws.send_json(AppState.interpret(data["command"]))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(e, flush=True)
