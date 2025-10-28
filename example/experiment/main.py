from threading import Thread
from time import sleep


def main():
    sleep(2)
    print("ended")


if __name__ == "__main__":
    t = Thread(target=main)
    t.start()
