import zmq
from typing import List, Tuple
from collections import OrderedDict
import os

class CommunicationZmq:
    context = None
    die = False
    finput = None
    localport = 0
    communication = None
    out_endpoints = set()

    def __init__(self, id: int) -> None:
        self.socket_ = self.context.socket(zmq.DEALER)
        self.socket_.setsockopt(zmq.RCVTIMEO, 1000)
        self.socket_.setsockopt(zmq.ROUTING_ID, ("edge" + str(id)).encode())

    def connect(self, host: str, port: int) -> bool:
        endpoint = "tcp://" + host + ":" + str(port)
        try:
            self.socket_.connect(endpoint)
            return True
        except zmq.error.ZMQError:
            return False

    def recv(self, buff: bytes, len: int) -> int:
        try:
            ret = self.socket_.recv(flags=zmq.NOBLOCK)
            ret_size = len(ret)
            ret.copy_to_memory(buff, len)
            print("s: ", ret_size)
            return ret_size
        except zmq.error.Again:
            return 0

    def recv_msg(self) -> Tuple[bytes, bytes]:
        try:
            routing_id = self.socket_.recv_string()
            if len(routing_id) == 0:
                return (None, None)
            message = self.socket_.recv()
            return (routing_id.encode(), message)
        except zmq.error.Again:
            return (None, None)

    def send(self, id: int, data: bytes) -> int:
        routing_id = "edge" + str(id)
        return self.send_msg(routing_id.encode(), data)

    def send_msg(self, routing_id: bytes, message: bytes) -> int:
        ret = self.socket_.send(routing_id, flags=zmq.SNDMORE)
        ret += self.socket_.send(message)
        return ret

    @classmethod
    def init(cls, finput, localport):
        cls.localport = localport
        cls.finput = finput
        cls.context = zmq.Context()
        cls.communication = CommunicationZmq(localport, True)
        for ep in cls.out_endpoints:
            cls.communication.connect(ep[0] + ".iccluster.epfl.ch", ep[1])

    @classmethod
    def add_endpoint(cls, host: str, port: int):
        cls.out_endpoints.add((host, port))

    @classmethod
    def send_all(cls, data: bytes) -> int:
        ret = 0
        for endpoint in cls.out_endpoints:
            ret += cls.send(endpoint[0], endpoint[1], data)
        return ret

    @classmethod
    def iterate(cls):
        endpoint = "tcp://*:" + str(cls.localport)
        cls.communication.socket_.bind(endpoint)
        while not cls.die:
            msg = cls.communication.recv_msg()
            if msg[0] is not None:
                if cls.finput is not None:
                    cls.finput(msg[0].decode(), msg[1])

    @classmethod
    def cleanup(cls):
        if cls.communication is not None:
            cls.communication.socket_.close()
        if cls.context is not None:
            cls.context.term()
