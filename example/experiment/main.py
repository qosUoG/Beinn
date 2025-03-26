import pkgutil
import uvicorn

# from lib.ExampleExperiment import ExampleExperiment
from app.main import app
from ttt.ttt import TTT


if __name__ == "__main__":
    ttt = TTT()
    ttt.run()
