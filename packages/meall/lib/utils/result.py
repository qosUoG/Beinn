from typing import Any
import traceback


def error(e: Exception):
    return {
        "success": False,
        "error": traceback.print_exc(e),
    }


def ok(value: Any = None):
    return {"success": True, "value": value}
