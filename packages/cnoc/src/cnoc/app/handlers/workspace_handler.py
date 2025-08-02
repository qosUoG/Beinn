import importlib
import inspect
import json
import pkgutil
from typing import TypedDict

from ..state.experiments import Experiments

from ..state.foundation import Foundation

from ...public.params import (
    AllParamTypes,
    CompositeParam,
    InstanceEquipmentParam,
    InstanceExperimentParam,
)

from ..state.equipments import Equipments

from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC
from websockets import ServerConnection

from ._ee import handlers as eeHandlers


async def workspaceHandler(ws: ServerConnection):
    Foundation.workspace_ws = ws
    async for message in ws:
        req = json.loads(message)

        command: str = req["command"]

        if command in eeHandlers.keys():
            await eeHandlers[command](ws, req["value"])
            continue
