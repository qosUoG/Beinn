import importlib
import json
from typing import override


from .foundation import Foundation

from ._ees import EEInstance, EEsABC


from ...public.experiment import ExperimentABC


def sendExperimentCommand(command: str, value: dict):
    Foundation.workspace_ws.send(
        json.dumps({"command": f"experiment:{command}", "value": value})
    )


class Experiments(EEsABC[ExperimentABC]):
    @classmethod
    @override
    def create(
        cls,
        name: str,
        module_str: str,
        cls_str: str,
    ):
        module = importlib.import_module(module_str)
        module = importlib.reload(module)

        super().instances[name] = EEInstance[ExperimentABC](
            instance=getattr(module, cls_str)(),
            module=module_str,
            cls=cls_str,
        )

        # Set all callbacks
        super().instances[name].instance._cnoc_on(
            "started",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "started"})
            ),
        )

        super().instances[name].instance._cnoc_on(
            "loop_start",
            lambda _: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "loop_start"})
            ),
        )

        super().instances[name].instance._cnoc_on(
            "loop_end",
            lambda loop_count: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand(
                    "loop_count", {"name": name, "loop_count": loop_count}
                )
            ),
        )

        super().instances[name].instance._cnoc_on(
            "paused",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "paused"})
            ),
        )

        super().instances[name].instance._cnoc_on(
            "stopped",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "stopped"})
            ),
        )

        super().instances[name].instance._cnoc_on(
            "completed",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "completed"})
            ),
        )

        super().instances[name].instance._cnoc_on(
            "chart_created",
            lambda config: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("chart_config", {"name": name, "config": config})
            ),
        )

        return super().instances[name]
