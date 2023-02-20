import machine_learning.mf_node
import node_protocol
from typing import List
import struct


protocol = node_protocol.NodeProtocol()


def multipart_deserialize(data: bytes) -> List[str]:
    ret = []
    cursor = 0
    while cursor < len(data):
        chunk_size = struct.unpack('Q', data[cursor:cursor + 8])[0]
        cursor += 8
        if chunk_size + cursor > len(data):
            print(f"multipart_deserialize: out of bounds. Chunk: {chunk_size} Cursor: {cursor} Data size: {len(data)}")
            break
        ret.append(data[cursor:cursor + chunk_size].decode('utf-8'))
        cursor += chunk_size
    return ret


def ecall_init(args):
    return protocol.init(args)


def ecall_input(data: bytes):
    protocol.input(multipart_deserialize(data))
