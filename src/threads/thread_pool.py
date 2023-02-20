import threading
import queue

class ThreadPool:
    def __init__(self, n):
        self.tasks = queue.Queue()
        self.workers = [threading.Thread(target=self.worker) for _ in range(n)]
        self.terminate = False
        for worker in self.workers:
            worker.start()

    def worker(self):
        while True:
            try:
                task = self.tasks.get(block=True, timeout=1)
            except queue.Empty:
                if self.terminate:
                    return
                else:
                    continue
            task()

    def add_task(self, t):
        with self.tasks.mutex:
            if self.terminate:
                raise RuntimeError("Adding task to a dying ThreadPool")
            self.tasks.put(t)

    def join(self):
        self.tasks.join()

    def terminate(self):
        self.terminate = True
        for _ in self.workers:
            self.add_task(None)
        for worker in self.workers:
            worker.join()
