import asyncio


class Foundation:
    _loop: asyncio.EventLoop

    @classmethod
    def getLoop(cls):
        return cls._loop

    @classmethod
    def setLoop(cls, loop: asyncio.EventLoop):
        cls._loop = loop
