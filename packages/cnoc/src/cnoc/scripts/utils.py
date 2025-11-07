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


class Runtime:
    def __init__(self):
        self.success = True

    def errFlush(self):
        print(flush=True, file=sys.stderr)

    def printResult(self, msg: str):
        print(msg, flush=True, file=sys.stdout)
        sys.exit(0 if self.success else 1)

    def printErr(self, msg: str):
        print(msg, flush=True, file=sys.stderr)
        self.success = False

    def end(self):
        sys.exit(0 if self.success else 1)
