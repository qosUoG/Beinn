import site
import sys


def preloadLocal():
    slash = "/" if "/" in __file__ else "\\"
    roots = __file__.split(slash)
    venv_index = roots.index(".venv")
    path = slash.join(roots[:venv_index])

    site.addsitedir(path)

    return roots[venv_index - 1]


def printErr(msg: str):
    print(msg, flush=True, file=sys.stderr)


def errFlush():
    print(end=None, flush=True, file=sys.stderr)
