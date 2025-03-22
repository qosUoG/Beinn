import importlib.util
import json
import sys
import ast
from typing import Any


def importFromStr(code):
    parsed = ast.parse(code)
    modulename = ""
    classname = ""
    for node in ast.walk(parsed):
        if isinstance(node, ast.ClassDef):
            classname = node.name
            modulename = node.name.lower()
            break

    spec = importlib.util.spec_from_loader(modulename, loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(code, module.__dict__)
    sys.modules[spec.name] = module
    return [module, classname]


def singleKVNumberMessage(key: str, value: float | int):
    return "{" + f'"key": "{key}", "value": {value}' + "}"


def singleKVStrMessage(key: str, value: str):
    return "{" + f'"key": "{key}", "value": "{value}"' + "}"


def singleKVDictMessage(key: str, value: dict[str, Any]):
    return json.dumps({"key": key, "value": value})
