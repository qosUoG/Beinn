import site


def preloadLocal():
    roots: list[str]
    if "/" in __file__:
        roots = __file__.split("/")
    elif "\\" in __file__:
        roots = __file__.split("\\")
    venv_index = roots.index(".venv")
    path = "/".join(roots[:venv_index])

    site.addsitedir(path)
