import json
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import pyvisa
from ws.backend import WsInMessageTypeUnion


app = FastAPI()
app.mount("/", StaticFiles(directory="dist", html=True), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    equipments = {}

    while True:
        data = await websocket.receive_text()
        decoded: WsInMessageTypeUnion = json.load(data)
        match decoded["command"]:
            case "Load-Equipment":
                for name, config in decoded["payload"].items():
                    with open(config["path"], mode="r", encoding="utf-8") as raw:
                        exec(raw.read())
                        exec(
                            f"equipments[name] = {config['classname']}({config['address']})"
                        )
