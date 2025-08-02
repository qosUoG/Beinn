import importlib
import json


from ...public.params import dict2Params


from .foundation import Foundation

from ._ees import EEInstance


from ...public.experiment import ExperimentABC


async def sendExperimentCommand(command: str, value: dict):
    await Foundation.workspace_ws.send(
        json.dumps({"command": f"experiment:{command}", "value": value})
    )


class Experiments:
    instances: dict[str, EEInstance[ExperimentABC]] = {}

    @classmethod
    def create(
        cls,
        name: str,
        module_str: str,
        cls_str: str,
    ):
        module = importlib.import_module(module_str)
        module = importlib.reload(module)

        cls.instances[name] = EEInstance[ExperimentABC](
            instance=getattr(module, cls_str)(),
            module=module_str,
            cls=cls_str,
        )

        # Set all callbacks
        cls.instances[name].instance._cnoc_on(
            "expected_loop_count",
            lambda expected_loop_count: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand(
                    "expected_loop_count",
                    {"name": name, "expected_loop_count": expected_loop_count},
                )
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "started",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "started"})
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "loop_start",
            lambda _: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "loop_start"})
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "loop_end",
            lambda loop_count: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand(
                    "loop_count", {"name": name, "loop_count": loop_count}
                )
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "paused",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "paused"})
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "stopped",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "stopped"})
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "completed",
            lambda: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("status", {"name": name, "status": "completed"})
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "chart_created",
            lambda config: Foundation.runCoroThreadsafeBlocking(
                sendExperimentCommand("chart_config", {"name": name, "config": config})
            ),
        )

        return cls.instances[name]

    @classmethod
    def updateParams(cls, name: str, params: dict):
        cls.instances[name].instance.params = dict2Params(params)

    @classmethod
    def remove(cls, name: str):
        del cls.instances[name]
