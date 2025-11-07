import importlib
import json
import sys
from traceback import print_tb
from .utils import preloadLocal, Runtime


from ..public._params import params2Dict

runtime = Runtime()


def main():
    try:
        preloadLocal()

        module = importlib.import_module(sys.argv[1])
        module = importlib.reload(module)

        instance = getattr(module, sys.argv[2])()

        runtime.printResult(
            json.dumps(
                {
                    "module": sys.argv[1],
                    "cls": sys.argv[2],
                    "params": params2Dict(instance.params),
                }
            )
        )

    except Exception as e:
        runtime.printErr(f"Error: {e}")
        _, _, traceback = sys.exc_info()
        print_tb(traceback, file=sys.stderr)
        runtime.errFlush()

    runtime.end()
