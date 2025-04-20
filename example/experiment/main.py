import asyncio
import os
import pickle
import pprint


def th():
    print(os.getpid())


async def main():
    print(os.getpid())
    await asyncio.to_thread(th)


if __name__ == "__main__":
    asyncio.run(main())
    # filename = "./data/ExampleSqlSaver.pickle"

    # with open(filename, "rb") as f:
    #     pprint.pprint(pickle.load(f))

    # Exec mode for multiple statements
