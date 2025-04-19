from fastapi import APIRouter
import os
from ..lib.settings.state import AppState


router = APIRouter()


@router.get("/workspace/status")
async def workspace_status():
    return {"status": "online"}


@router.get("/workspace/forcestop")
async def workspace_forcestop():
    await AppState.forceStop()
    return {"success": True}

@router.get("workspace/pid")
async def workspace_pid():
    return {"pid": os.getpid()}