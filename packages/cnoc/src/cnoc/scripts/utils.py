import site


def preloadLocal():
    slash = "/" if "/" in __file__ else "\\"
    roots = __file__.split(slash)
    venv_index = roots.index(".venv")
    path = slash.join(roots[:venv_index])

    site.addsitedir(path)

    return path
