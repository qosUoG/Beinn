import pkgutil


if __name__ == "__main__":
    import experiment.abcde

    for package in pkgutil.iter_modules():
        if "abcde" in package.name:
            print(package.name)
