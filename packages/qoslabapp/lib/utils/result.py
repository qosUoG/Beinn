from typing import Any


def userError(error: str):
    return {"success": False, "err": {"type": "USER", "error": error}}


def applicationError(error: str):
    return {"success": False, "err": {"type": "APPLICATION", "error": error}}


def ok(value: Any = None):
    return {"success": True, "value": value}
