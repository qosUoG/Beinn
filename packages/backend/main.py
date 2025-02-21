from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread
import os
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from lib.params import AllParamTypes


class AppState:
    equipments = {}
    experiments_threads: dict[str, Thread] = {}


app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/getDirectoryContent/{dir:path}")
async def readDir(dir: str):
    """
    Reads the content of a directory
    """
    print(dir)
    res = []
    with os.scandir(dir) as it:
        for entry in it:
            if not entry.name.startswith(".") and entry.is_file():
                res.append(entry.name)

    return res


class StartExperimentPayload(BaseModel):
    path: str
    methodname: str
    params: dict[str, AllParamTypes]


@app.post("/startExperiment")
async def startExperiment(payload: StartExperimentPayload):
    """
    Start Experiment
    """
    with open(payload.path, mode="r", encoding="utf-8") as raw:
        # Read the definition code from the source file
        exec(raw.read())
        # Create the experiment in a separate thread
        exec(
            f"AppState.experiment_threads['{payload.methodname}'] = Thread(target={payload.methodname}, args={payload.params})"
        )
        # Start running the experiment
        exec(f"AppState.experiment_threads['{payload.methodname}'].start()")


class LoadEquipmentPayload(BaseModel):
    class EquipmentValue(BaseModel):
        name: str
        address: str
        path: str
        classname: str

    equipments: list[EquipmentValue]


@app.post("/loadEquipment")
async def loadEquipment(payload: LoadEquipmentPayload):
    AppState.equipments.clear()
    for equipment in payload.equipments:
        with open(equipment.name, mode="r", encoding="utf-8") as raw:
            # Read the definition code from the source file
            exec(raw.read())
            # Initilize the equipment and assign to equipments dict
            exec(
                f"equipments[{equipment.name}] = {equipment.classname}({equipment.address})"
            )


app.mount("/", StaticFiles(directory="static", html=True), name="static")
