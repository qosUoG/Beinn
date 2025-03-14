from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from packages.qoslabapp.routers import workspace

from .routers import equipment, experiment


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

app.include_router(equipment.router)
app.include_router(experiment.router)
app.include_router(workspace.router)
