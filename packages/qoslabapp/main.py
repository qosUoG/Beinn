import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .lib.settings.foundation import Foundation

from .lib.settings.state import AppState


from .routers import equipment, experiment, workspace, chart


@asynccontextmanager
async def lifespan(app: FastAPI):
    Foundation.setLoop(asyncio.get_running_loop())
    yield
    await AppState.cleanup()


app = FastAPI(lifespan=lifespan)

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

app.include_router(equipment.router)
app.include_router(experiment.router)
app.include_router(workspace.router)
app.include_router(chart.router)
