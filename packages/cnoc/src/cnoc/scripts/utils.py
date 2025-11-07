import os
import site
import sys


def preloadLocal():
    slash = "/" if "/" in __file__ else "\\"
    roots = __file__.split(slash)
    venv_index = roots.index(".venv")
    path = slash.join(roots[:venv_index])

    site.addsitedir(path)

    res = [
        f
        for f in os.listdir(path)
        if os.path.isdir(path + slash + f) and not f.startswith((".", "__"))
    ]

    res.extend(
        [
            f.split(".")[0]
            for f in os.listdir(path)
            if f.endswith(".py") and not f.startswith((".", "__"))
        ]
    )

    # possible local packages
    return res


def printErr(msg: str):
    print(msg, flush=True, file=sys.stderr)


def errFlush():
    print(end=None, flush=True, file=sys.stderr)
