import threading
import queue
import time
import hashlib
import base64
import math
import statistics

class ThreadPool:
    def __init__(self, n):
        self.tasks = queue.Queue()
        self.workers = []
        self.terminate = False
        for i in range(n):
            self.workers.append(threading.Thread(target=self.worker))
            self.workers[-1].start()

    def worker(self):
        while True:
            with self.tasks.mutex:
                self.tasks.not_empty.wait_for(lambda: self.terminate or not self.tasks.empty())
            if self.terminate:
                return
            task = self.tasks.get()
            task()

    def add_task(self, t):
        with self.tasks.mutex:
            if self.terminate:
                raise RuntimeError("Adding task to a dying ThreadPool")
            self.tasks.put(t)
            self.tasks.not_empty.notify()

    def __del__(self):
        with self.tasks.mutex:
            self.terminate = True
            self.tasks.not_empty.notify_all()
        for worker in self.workers:
            worker.join()

class TimeProbe:
    def __init__(self, r):
        if r == "SECONDS":
            self.multiplier = 1
        elif r == "MILI":
            self.multiplier = 1e+3
        elif r == "MICRO":
            self.multiplier = 1e+6
        elif r == "NANO":
            self.multiplier = 1e+9

        # calculate hash
        self.hash = self.__hash()

    def __hash(self):
        me = bytes(str(id(self)), "utf-8")
        return base64.b64encode(hashlib.sha224(me).digest()).decode()

    def start(self):
        global start
        start = time.monotonic()

    def stop(self):
        end = time.monotonic()
        return (end - start) * self.multiplier

class TimeProbeStats:
    def __init__(self):
        # calculate hash
        self.hash = self.__hash()

        # initialize statistics
        self.accum = []

    def __hash(self):
        me = bytes(str(id(self)), "utf-8")
        return base64.b64encode(hashlib.sha224(me).digest()).decode()

    def start(self):
        self.probe = TimeProbe("NANO")
        self.probe.start()

    def stop(self):
        elapsed_time = self.probe.stop()
        self.accum.append(elapsed_time)
        return elapsed_time

    def summary(self, title):
        count = len(self.accum)
        mean = statistics.mean(self.accum)
        stdev = statistics.stdev(self.accum)
        total = sum(self.accum)
        return f"{title}\t{count}\t{mean}\t{stdev}\t{total}"
