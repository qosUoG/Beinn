import pkgutil


class TTT:
    def run(self):
        for package in pkgutil.walk_packages():
            if package.name.startswith("lib"):
                print(package.name)
