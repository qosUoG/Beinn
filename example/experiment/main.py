import inspect
import examplelib


if __name__ == "__main__":
    for [name, _] in inspect.getmembers(examplelib.ExampleDriver):
        print(name)
