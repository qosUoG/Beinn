from asyncio import Task
import asyncio
from sqlite3 import Connection, Cursor
import sqlite3
from threading import Event, Lock
import time

from typing import override
from fastapi import WebSocket
from qoslablib import (
    exceptions as e,
    chart as c,
    saver as s,
    runtime as r,
)


class ChartHandler[FrameT]:
    def __init__(self, title: str, chart: c.ChartABC):
        self.title = title
        self.frames: list[FrameT] = []
        self.chart = chart

        self._lock = Lock()

        self.rate = 1
        self.connections: list[WebSocket] = []

        self.has_listener = Event()

        def _plot_fn(frame: FrameT):
            if not AppState.charts[title].has_listener.is_set():
                with AppState.charts[title]._lock():
                    AppState.charts[title].frames.append(frame)

        self.chart._plot_fn = _plot_fn


class SqlSaverHandler[FrameT]:
    def __init__(self, title: str, sql_saver: s.SqlSaverABC):
        self.title = title
        self.frames: list[FrameT] = []
        self.sql_saver = sql_saver
        self._lock = Lock()

        # Create table with name and timestamp (ms)
        table_name = f'"{self.title} timestamp:{self.sql_saver.getConfig().timestamp}"'
        print(f"""
BEGIN;
CREATE TABLE {table_name}({self.sql_saver.getColumns()});
COMMIT;
""")

        AppState.sqlite3_cursor.executescript(
            f"""
BEGIN;
CREATE TABLE {table_name}({self.sql_saver.getColumns()});
COMMIT;
"""
        )

        def _save_fn(frame: FrameT):
            with AppState.sql_savers[title]._lock():
                AppState.sql_savers[title].frames.append(frame)

        self.sql_saver._save_fn = _save_fn


class AppState(c.ChartHolderABC, s.SqlSaverHolderABC):
    project = {"path": ""}
    equipments: dict[str, r.EquipmentABC] = {}
    experiments: dict[str, r.ExperimentABC] = {}
    experiment_tasks: dict[str, Task] = {}
    experiment_stop_events: dict[str, Event] = {}
    experiment_pause_events: dict[str, Event] = {}

    charts: dict[str, ChartHandler]
    sql_savers: dict[str, SqlSaverHandler]

    sql_worker_task: Task
    sql_worker_task_created = False

    class SqlWorker:
        sqlite3_connection: Connection
        sqlite3_cursor: Cursor
        sqlite3_continuous_insert: Event

        @classmethod
        def createSqlConnection(cls):
            cls.sqlite3_connection = sqlite3.connect("data.db")
            cls.sqlite3_cursor = cls.sqlite3_connection.cursor()

        @classmethod
        def continuousSqlInsertWorker(cls):
            time.sleep(5)
            for sql_saver_handler in AppState.sql_savers.values():
                with sql_saver_handler._lock():
                    for frame in sql_saver_handler.frames:
                        cls.sqlite3_cursor.execute(
                            sql_saver_handler.sql_saver.getInsertSqlTemplate(),
                            frame,
                        )

            cls.sqlite3_connection.commit()

    @classmethod
    def _startSqlWorker(cls):
        if cls.sql_worker_task_created:
            return

        def sqlWorker():
            sqlWorker = AppState.SqlWorker()
            sqlWorker.createSqlConnection()
            while True:
                sqlWorker.continuousSqlInsertWorker()

        # Start the thread that continuously check for data to commit
        cls.sql_worker_task = asyncio.create_task(asyncio.to_thread(sqlWorker))

    @classmethod
    @override
    def createSqlSaver(cls, sql_saverT: type[s.SqlSaverABC], *, kwargs={}):
        # Create database connection if not yet created
        cls._startSqlWorker

        title = kwargs["title"]
        cls.sql_savers[title] = SqlSaverHandler(title, sql_saverT(**kwargs))
        return cls.sql_savers[title].sql_saver

    @classmethod
    @override
    def createChart(cls, chartT: type[c.ChartABC], *, kwargs={}):
        # The title should be unique
        title = kwargs["title"]
        cls.charts[title] = ChartHandler(title, chartT(**kwargs))
        return cls.charts[title].chart

    @classmethod
    def run_experiment(cls, name: str):
        cls.experiment_stop_events[name] = Event()
        cls.experiment_pause_events[name] = Event()
        cls.experiment_tasks[name] = asyncio.create_task(
            asyncio.to_thread(
                _experiment_runner,
                cls.experiments[name],
                cls.experiment_stop_events[name],
                cls.experiment_pause_events[name],
            )
        )

    @classmethod
    def pause_experiment(cls, name: str):
        cls.experiment_pause_events[name].set()

    @classmethod
    def continue_experiment(cls, name: str):
        cls.experiment_pause_events[name].clear()

    @classmethod
    def stop_experiment(cls, name: str):
        cls.experiment_stop_events[name].set()


def _experiment_runner(
    experiment: r.ExperimentABC, stop_event: Event, pause_event: Event
):
    # First run the inialize method
    experiment.initialize()

    index = 0
    while True:
        if stop_event.is_set():
            print("experiment stopped")
            experiment.stop()
            return

        if not pause_event.is_set():
            try:
                experiment.loop(index)
                index += 1

            except e.ExperimentEnded:
                print("experiment ended")
                return
