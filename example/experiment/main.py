import sys
from threading import Thread
from time import sleep


def t():
    while True:
        sleep(0.5)
        print("Hello")


def main():
    thread = Thread(target=t)
    thread.start()
    sleep(2)
    print("Killing")

    sys.exit()


if __name__ == "__main__":
    main()
