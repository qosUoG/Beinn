from fastapi import APIRouter
import os

from pydantic import BaseModel

from lib.state import AppState


router = APIRouter()


class Path(BaseModel):
    path: str


@router.post("/workspace/set_directory")
async def set_directory(body: Path):
    """
    Set and Reads the content of a directory
    """
    print(body)
    path = body.path
    AppState.project["path"] = path

    res = []
    with os.scandir(path) as it:
        for entry in it:
            if not entry.name.startswith(".") and entry.is_file():
                res.append(entry.name)

    return res
