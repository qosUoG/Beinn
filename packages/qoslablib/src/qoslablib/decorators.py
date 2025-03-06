import functools
from threading import Lock


def Experiment(cls):
    cls._qoslab_type = "experiment"
    return cls


def Equipment(cls):
    cls._qoslab_type = "equipment"
    init = cls.__init__

    def __init__(self, *args, **kws):
        self._qoslab_equipment_thread_lock = Lock()
        init(self, *args, **kws)

    cls.__init__ = __init__
    return cls


def EquipmentTLock(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._qoslab_equipment_thread_lock:
            func(*args, **kwargs)
            return func(*args, **kwargs)

    return wrapper
