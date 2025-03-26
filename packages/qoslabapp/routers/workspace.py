from fastapi import APIRouter

from ..lib.settings.state import AppState


router = APIRouter()


@router.get("/workspace/status")
async def workspace_status():
    return {"status": "online"}


@router.get("/workspace/forcestop")
async def workspace_forcestop():
    await AppState.forceStop()
    return {"forcestop": "success"}
