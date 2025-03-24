import asyncio
from sqlite3 import Connection, Cursor
import sqlite3
from threading import Event
from time import sleep

from ..proxies.sql_saver import SqlSaverProxy


class SqlWorker:
    _sqlite3_connection: Connection
    _sqlite3_cursor: Cursor

    _proxies: dict[str, dict[str, SqlSaverProxy]] = []

    _sql_worker_task: asyncio.Task
    _sql_worker_task_created: bool = False
    _sql_connected = Event()

    @classmethod
    def createSqlConnection(cls):
        cls._sqlite3_connection = sqlite3.connect("data.db")
        cls._sqlite3_cursor = cls._sqlite3_connection.cursor()
        cls._sql_connected.set()

    @classmethod
    def startSqlWorker(cls, proxies):
        cls._proxies = proxies

        if cls._sql_worker_task_created:
            return

        # Start the thread that continuously check for data to commit
        cls._sql_worker_task = asyncio.create_task(asyncio.to_thread(cls.sqlWorker))

        cls._sql_worker_task_created = True

    @classmethod
    def runSql(cls, sql: str):
        print(sql)
        cls._sqlite3_cursor.executescript(sql)

    @classmethod
    def sqlWorker(cls):
        cls.createSqlConnection()
        while True:
            sleep(5)
            for sql_saver_proxies in cls._proxies.values():
                for sql_saver_proxy in sql_saver_proxies.values():
                    cls._sqlite3_cursor.executemany(
                        sql_saver_proxy.getInsertSql(),
                        sql_saver_proxy.toOwnedFrames(),
                    )

            cls._sqlite3_connection.commit()
