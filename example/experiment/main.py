import asyncio
import sys
from threading import Thread
from time import sleep


global x, task
x = 0


def tt():
    sleep(2)
    print("ended tt")
    global x
    x = 1


async def t():
    global x
    print("t")
    await asyncio.to_thread(tt)
    print(x)
    x = 2
    print("t ended")
    # print("ended", flush=True)
    # sys.exit()


def done(_: asyncio.Task):
    global task, x
    print(task.done())
    print("done", x)
    # sys.exit()


async def parallel():
    global x
    print("parallel", x)
    await asyncio.sleep(1)
    print("parallel", x)
    await asyncio.sleep(1)
    print("parallel", x)
    await asyncio.sleep(1)
    print("parallel", x)


async def separate():
    global task
    task = asyncio.create_task(t())
    task.add_done_callback(done)
    print("main", x)

    # await asyncio.gather(parallel())


async def main():
    global task
    await separate()
    await asyncio.gather(task)


if __name__ == "__main__":
    asyncio.run(main())
    sleep(3)
