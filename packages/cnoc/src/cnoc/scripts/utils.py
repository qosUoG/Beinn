import os
import site
import sys


def preloadLocal():
    slash = "/" if "/" in __file__ else "\\"
    roots = __file__.split(slash)
    venv_index = roots.index(".venv")
    path = slash.join(roots[:venv_index])

    site.addsitedir(path)

    # possible local packages
    return [
        f
        for f in os.listdir(path)
        if os.path.isdir(path + slash + f) and not f.startswith((".", "__"))
    ]


def printErr(msg: str):
    print(msg, flush=True, file=sys.stderr)


def errFlush():
    print(end=None, flush=True, file=sys.stderr)
