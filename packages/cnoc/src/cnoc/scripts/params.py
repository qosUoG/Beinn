import importlib
import json
import sys

from ..public.params import cnoc_params2Dict


def main():
    module = importlib.import_module(sys.argv[1])
    module = importlib.reload(module)

    instance = getattr(module, sys.argv[2])()

    print(
        json.dumps(
            {
                "module": sys.argv[1],
                "cls": sys.argv[2],
                "params": cnoc_params2Dict(instance.params),  # type: ignore
            }
        )
    )
