from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..lib.settings.state import AppState


router = APIRouter()


@router.websocket("/cli")
async def cli(ws: WebSocket):
    # This websocket shall keep accepting code and post back result of the code
    await ws.accept()
    try:
        while True:
            try:
                data = await ws.receive_json()
            except Exception as e:
                print(e, flush=True)

            if data["type"] == "general":
                await ws.send_json(AppState.interpret(data["code"]))
            else:
                await ws.send_json(AppState.eqiupment_interpret(**data))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(e, flush=True)
