from abc import ABC, abstractmethod
import time
from typing import Callable, override

from pydantic import BaseModel


class SqlSaverABC(ABC):
    class AbstractConfig(BaseModel):
        # ms
        timestamp: int

    @abstractmethod
    def save(self, frame) -> None:
        # This method saves one frame of data
        raise NotImplementedError

    @abstractmethod
    def getConfig(self) -> AbstractConfig:
        # This function returns the config of the saver
        raise NotImplementedError

    @abstractmethod
    def getInsertSqlTemplate(self) -> str:
        # This function gets the insert sql query
        raise NotImplementedError

    @abstractmethod
    def getColumns(self) -> str:
        # This function returns the string used for the sql creating table
        raise NotImplementedError


class SqlSaverHolderABC(ABC):
    # The holder shall manage the database connection, and provide a method that would be consumed bu the SaverABC method

    @classmethod
    @abstractmethod
    def createSqlSaver(cls, sql_saverT: type[SqlSaverABC], *, kwargs={}) -> SqlSaverABC:
        # This method returns a plot object
        raise NotImplementedError


class XYSqlSaver(SqlSaverABC):
    class Config(BaseModel):
        title: str
        x_name: str
        y_names: list[str]
        timestamp: int

    def __init__(
        self,
        *,
        title: str,
        x_name: str,
        y_names: list[str],
        save_fn: Callable[[dict[str, float]], None],
    ):
        self.title = (title,)
        self.x_name = x_name
        self.y_names = y_names
        self._save_fn = save_fn

        self.config: XYSqlSaver.Config = {
            "title": self.title,
            "x_name": self.x_name,
            "y_names": self.y_names,
            "timestamp": int(time.time() * 1000),
        }

        self._save_fn = save_fn

    @override
    def getConfig(self) -> Config:
        return self.config

    @override
    def getColumns(self) -> str:
        res = "timestamp INTEGER PRIMARY KEY"
        res += f",\n{self.x_name} REAL"
        for y_name in self.y_names:
            res += f",\n{y_name} REAL"

        return res

    @override
    def save(self, frame):
        self._save_fn(frame)
