from fastapi import APIRouter


router = APIRouter()


@router.get("workspace/status")
def workspace_status():
    return {"status": "online"}
