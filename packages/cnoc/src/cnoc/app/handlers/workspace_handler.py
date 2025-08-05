from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import sys
from traceback import print_tb

from ..state.equipments import Equipments


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
                        continue
                    case "pause":
                        Experiments.instances[name].instance._cnoc_pause()
                        continue
                    case "stop":
                        Experiments.instances[name].instance._cnoc_stop()
                        continue
                    case "continue":
                        Experiments.instances[name].instance._cnoc_continue()
                        continue

            if command.startswith("interpret:"):
                code: str = req["value"]["code"]
                if command.split(":")[1] == "equipment":
                    name = req["value"]["name"]
                    code = code.replace(name, f"Equipments.instances[{name}].instance")

                    try:
                        print(
                            f"{eval(code, globals=globals())}",
                            flush=True,
                        )
                        continue

                    except SyntaxError:
                        pass
                    except Exception as e:
                        print(e, flush=True)
                        continue

                    try:
                        f = StringIO()

                        with redirect_stdout(f):
                            with redirect_stderr(sys.stdout):
                                exec(code, globals=globals())

                        continue

                    except Exception as e:
                        print(e, flush=True)
                        continue

            print(f"Unknown command {command}", flush=True)

        except Exception as e:
            print(f"Exception in workspace handler: {e}", flush=True)
            _, _, traceback = sys.exc_info()
            print_tb(traceback)
            print(end=None, flush=True)
            continue
