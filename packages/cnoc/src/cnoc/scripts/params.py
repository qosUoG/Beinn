import importlib
import sys


def main():
    module = importlib.import_module(sys.argv[1])
    module = importlib.reload(module)

    instance = getattr(module, sys.argv[2])()
    print(instance.params)
