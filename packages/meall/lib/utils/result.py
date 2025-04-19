from typing import Any
import traceback


def userError(error: str):
    return {"success": False, "err": {"type": "USER", "error": error}}


def applicationError(e: Exception):
    return {
        "success": False,
        "err": {"type": "APPLICATION", "error": traceback.print_exc(e)},
    }


def ok(value: Any = None):
    return {"success": True, "value": value}
