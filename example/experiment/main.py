import asyncio
from time import sleep
from typing import Any

tasks: list[asyncio.Task[Any]] = []


async def tt():
    await asyncio.sleep(1)
    print("tt done")


def th(loop: asyncio.AbstractEventLoop):
    sleep(1)
    print("th")

    def tt_callback():
        tasks.append(asyncio.create_task(tt()))

    loop.call_soon_threadsafe(tt_callback)
    print("th done")


async def async_main():
    print("async_main")
    await asyncio.to_thread(th, asyncio.get_running_loop())
    await asyncio.sleep(1)
    print("async_main done")
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(async_main())
