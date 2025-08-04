import json


from ..state.experiments import Experiments

from ..state.foundation import Foundation


from websockets import ServerConnection

from ._ee import handlers as eeHandlers


async def workspaceHandler(ws: ServerConnection):
    Foundation.workspace_ws = ws

    async for message in ws:
        try:
            req = json.loads(message)
            command: str = req["command"]

            if command in eeHandlers.keys():
                await eeHandlers[command](ws, req["value"])
                continue

            if command.startswith("experiment:"):
                name = req["value"]["name"]
                if name not in Experiments.instances:
                    print(f"Experiment {name} does not exist", flush=True)
                    continue

                match command.split(":")[1]:
                    case "start":
                        await Experiments.instances[name].instance._cnoc_start()
                    case "pause":
                        Experiments.instances[name].instance._cnoc_pause()
                    case "stop":
                        Experiments.instances[name].instance._cnoc_stop()
                    case "continue":
                        Experiments.instances[name].instance._cnoc_continue()

                continue
        except Exception as e:
            print(f"Exception in workspace handler: {e}", flush=True)
            continue
