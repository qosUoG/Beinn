from fastapi import APIRouter
import os

from ..lib.utils.result import ok
from ..lib.settings.state import AppState


router = APIRouter()


@router.get("/workspace/online")
async def workspace_status():
    return ok()


@router.get("/workspace/kill")
async def workspace_forcestop():
    await AppState.kill()
    return ok()


@router.get("/workspace/pid")
async def workspace_pid():
    return ok(os.getpid())
