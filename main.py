import datetime
import signal
import time

KEEP_GOING = True


def stop_keep_going(signum, frame):
    global KEEP_GOING
    print(f"Got signal {signum}")
    KEEP_GOING = False


if __name__ == "__main__":

    print("hello world")

    signal.signal(signal.SIGTERM, stop_keep_going)

    while KEEP_GOING:
        print(datetime.datetime.now())
        time.sleep(3)
