import importlib

from packages.cnoc.src.cnoc.app.utils.messenger import kv2str

from .foundation import Foundation

from .ees import EEInstance

from ...public.params import dict2Param, param2Dict
from ...public.experiment import ExperimentABC


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
            "started",
            lambda: Foundation.runCoroThreadsafeBlocking(
                Foundation.workspace_ws.send(kv2str("status", "started"))
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "loop_start",
            lambda iteration_count: Foundation.runCoroThreadsafeBlocking(
                Foundation.workspace_ws.send(kv2str("status", "loop_start"))
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "loop_end",
            lambda iteration_count: Foundation.runCoroThreadsafeBlocking(
                Foundation.workspace_ws.send(kv2str("iteration_count", iteration_count))
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "paused",
            lambda: Foundation.runCoroThreadsafeBlocking(
                Foundation.workspace_ws.send(kv2str("status", "paused"))
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "stopped",
            lambda: Foundation.runCoroThreadsafeBlocking(
                Foundation.workspace_ws.send(kv2str("status", "stopped"))
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "completed",
            lambda: Foundation.runCoroThreadsafeBlocking(
                Foundation.workspace_ws.send(kv2str("status", "completed"))
            ),
        )

        cls.instances[name].instance._cnoc_on(
            "chart_created",
            lambda config: Foundation.runCoroThreadsafeBlocking(
                Foundation.workspace_ws.send(kv2str("chart_config", config))
            ),
        )

        return param2Dict(cls.instances[name].instance.params)

    @classmethod
    def save(cls, name: str, params: dict):
        cls.instances[name].instance.params = dict2Param(params)

    @classmethod
    def remove(cls, name: str):
        del cls.instances[name]
