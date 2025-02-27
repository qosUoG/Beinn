import importlib.util
import sys
import ast


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
