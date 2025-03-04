from fastapi import APIRouter

from ..lib.utils import importFromStr


router = APIRouter()


@router.get("/experiment/get_params/{filepath:path}")
async def get_params(filepath: str):
    with open(filepath, mode="r", encoding="utf-8") as raw:
        [module, classname] = importFromStr(raw.read())
        _class = getattr(module, classname)

        return _class.params


# class StartExperimentPayload(BaseModel):
#     path: str
#     methodname: str
#     params: dict[str, AllParamTypes]


# @router.post("/experiment/start")
# async def startExperiment(payload: StartExperimentPayload):
#     """
#     Start Experiment
#     """
#     with open(payload.path, mode="r", encoding="utf-8") as raw:
#         # Read the definition code from the source file
#         exec(raw.read())
#         # Create the experiment in a separate thread
#         exec(
#             f"AppState.experiment_threads['{payload.methodname}'] = Thread(target={payload.methodname}, args={payload.params})"
#         )
#         # Start running the experiment
#         exec(f"AppState.experiment_threads['{payload.methodname}'].start()")
