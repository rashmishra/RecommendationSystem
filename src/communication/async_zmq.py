from threading import Thread
from queue import Queue
import zmq
import socket
import os
import time
import stdatomic
from typing import Callable

class AsyncZmq:
    die = stdatomic.atomic(False)
    callbacks_ = {}
    callbackmap_mtx_ = threading.Lock()

    def __init__(self, endpoint: str, idprefix: str):
        self.context_ = zmq.Context(1)
        self.frontend_ = self.context_.socket(zmq.ROUTER)
        self.backend_ = self.context_.socket(zmq.ROUTER)
        hostname = socket.gethostname()
        self.frontend_.setsockopt(zmq.RCVBUF, 0)
        self.frontend_.setsockopt(zmq.ROUTING_ID, (idprefix + hostname).encode())
        self.frontend_.setsockopt(zmq.PROBE_ROUTER, 1)
        self.frontend_.connect("tcp://" + endpoint)
        NetStats.add_bytes_out(len(self.frontend_.getsockopt(zmq.ROUTING_ID)))
        self.backend_.bind("ipc://backend.ipc")
        self.worker_queue_ = Queue()
        self.outqueue_ = Queue()
        self.oqueue_mtx_ = threading.Lock()
        self.serverid_ = ""
        self.serverid_mtx_ = threading.Lock()
        self.thread_list_ = []
        self.thread_list_.append(Thread(target=self.worker_thread))
        self.thread_list_.append(Thread(target=self.handle_backend))
        self.thread_list_.append(Thread(target=self.handle_frontend))

        for thread in self.thread_list_:
            thread.start()

    def finish(self):
        AsyncZmq.die.store(True)

    @staticmethod
    def add_callback(id: int, cb: Callable[[str], None]):
        with AsyncZmq.callbackmap_mtx_:
            AsyncZmq.callbacks_[id] = cb

    @staticmethod
    def worker_thread():
        context = zmq.Context(1)
        worker = context.socket(zmq.REQ)
        worker.setsockopt(zmq.RCVBUF, 0)
        worker.setsockopt(zmq.ROUTING_ID, ("worker" + str(id)).encode())
        worker.connect("ipc://backend.ipc")
        while not AsyncZmq.die.load():
            r = "READY"
            worker.send_string(r)
            msg = internal_recv_multipart(worker)
            if len(msg) == 1:
                continue  # probe msg or suicide request
            prefix = "internal"
            if msg[1].startswith(prefix):
                rank = int(msg[1][len(prefix):])
                callback = None
                with AsyncZmq.callbackmap_mtx_:
                    if rank in AsyncZmq.callbacks_:
                        callback = AsyncZmq.callbacks_[rank]
                if callback:
                    try:
                        callback(unpack(str(msg[-1]), t))
                    except KeyError as e:
                        print("\033[31m{}\033[0m".format(str(e)))
                else:
                    print("Could not find a suitable callback for rank " + str(rank))
            else:
                print("Unknown destination: " + str(msg[1]))

    def send_standing_messages(self):
        ret = 0
        if not self.serverid_:
            return ret
        while True:
            with self.oqueue_mtx_:
                if self.outqueue_.empty():
                    break
                next_item = self.outqueue_.get()
            next_msg = next_item[1]
            ret += self.send_more(self.serverid_, False)
            ret +=
