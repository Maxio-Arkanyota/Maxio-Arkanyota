import fcntl
import sys
import threading
import os
import termios
import tty
from select import select

from main_terminalGetKey import getKey


class Raw(object):
    """Set raw input mode for device"""

    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)


class Nonblocking(object):
    """Set nonblocking mode for device"""

    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

"""
In [24]: input_key = ""
    ...: clean_key = ""
    ...: while True:
    ...:     with Raw(sys.stdin):
    ...:         if not select([sys.stdin], [], [], 0.1)[0]:
    ...:             continue
    ...:         input_key += sys.stdin.read(1)
    ...:         if input_key == "\033":
    ...:             with Nonblocking(sys.stdin):
    ...:                 input_key += sys.stdin.read(20)
    ...:                 if input_key.startswith("\033[<"):
    ...:                     _ = sys.stdin.read(1000)
    ...:         if input_key == "\033":
    ...:             clean_key = "escape"
    ...:         elif input_key == "\\":
    ...:             clean_key = "\\"
    ...:# clean input_key et clean_key 
    ...:     print(f"{input_key=}, {clean_key=}")

"""
class Key:
    stopping = False
    started = False
    thread: threading.Thread

    @classmethod
    def start(self):
        self.thread = threading.Thread(target=self._getkey)
        self.started = True
        self.stopping = False
        self.thread.start()

    @classmethod
    def stop(self):
        if self.started and self.thread.is_alive():
            self.stopping = True
            self.started = False

    @classmethod
    def _getkey(self):
        i = 0
        while not self.stopping:
            i += 1
            print(f"\033[13;13H{i}{self.stopping}")
            key = getKey()
            if key == "a":
                print("\033[5;5HHe press A")
            elif key == "q" or key == "\x03":
                clean_quit()

class Collector:
    stopping = False
    started = False
    thread: threading.Thread

    @classmethod
    def start(self):
        self.thread = threading.Thread(target=self._runner)
        self.started = True
        self.stopping = False
        self.thread.start()

    @classmethod
    def stop(self):
        if self.started and self.thread.is_alive():
            self.stopping = True
            self.started = False

    @classmethod
    def _runner(self):
        j = 0
        while not self.stopping:
            j += 1
            print(f"\033[14;14H{j}{self.stopping}")
            pass


def clean_quit(error: int = 0):
    Key.stop()
    Collector.stop()
    SystemExit(error)


def clear():
    print("\033[2J\033[1;1H")  # Clear screen


def main():
    clear()
    Key.start()
    Collector.start()


if __name__ == "__main__":
    main()
