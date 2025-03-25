from fastapi import APIRouter

from ..lib.settings.state import AppState


router = APIRouter()


@router.get("/workspace/status")
async def workspace_status():
    return {"status": "online"}


@router.get("/workspace/cleanup")
async def workspace_cleanup():
    await AppState.cleanup()
    return {"cleanup": "success"}
