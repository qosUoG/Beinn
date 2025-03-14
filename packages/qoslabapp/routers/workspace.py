from fastapi import APIRouter


router = APIRouter()


@router.get("/workspace/status")
async def workspace_status():
    return {"status": "online"}
