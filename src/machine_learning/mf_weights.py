from typing import List, Tuple
import numpy as np
from scipy.sparse import coo_matrix

Embedding = Tuple[float, List[float]]

class MFWeights:
    def __init__(self):
        self.users = None
        self.user_biases = None
        self.items = None
        self.item_biases = None
    
    def has(self, i: int, m: coo_matrix) -> bool:
        return i < m.shape[1] and m.getcol(i).nnz != 0
    
    def get_factors(self, i: int, factors: coo_matrix,
                    bias: coo_matrix) -> Embedding:
        ret = []
        v = factors.getcol(i).toarray()
        n = v.shape[0]
        for i in range(n):
            ret.append(v[i, 0])
        return (bias[0, i], ret)
    
    def has_item(self, item: int) -> bool:
        return self.has(item, self.items)
    
    def has_user(self, user: int) -> bool:
        return self.has(user, self.users)
    
    def get_item_factors(self, item: int) -> Embedding:
        return self.get_factors(item, self.items, self.item_biases)
    
    def get_user_factors(self, user: int) -> Embedding:
        return self.get_factors(user, self.users, self.user_biases)
    
    def predict(self, user: int, item: int) -> float:
        if user < 0 or item < 0:
            print(f"Invalid index ({user},{item})")
            raise ValueError
        assert self.users.shape[0] == self.items.shape[0]
        return (self.users.getcol(user).T @ self.items.getcol(item)).toarray()[0, 0] + \
               self.user_biases[0, user] + self.item_biases[0, item]
    
    def estimate_serial_size(self) -> int:
        return (self.serial_size(self.users) + self.serial_size(self.items) +
                self.serial_size(self.user_biases) + self.serial_size(self.item_biases))
    
    def serialize_with_size(self, matrix: coo_matrix) -> bytes:
        index = len(matrix.data.tobytes())
        nptr = index.to_bytes(8, byteorder='little')
        data = matrix.tocoo().todata()
        out = np.concatenate([nptr, data])
        return out
    
    def serialize(self) -> bytes:
        out = self.serialize_with_size(self.users)
        out += self.serialize_with_size(self.items)
        out += self.serialize_with_size(self.user_biases)
        out += self.serialize_with_size(self.item_biases)
        return out
    
    def deserialize_matrix(self, matrix: coo_matrix,
                           data: bytes, offset: int) -> int:
        size = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        matrix.data = np.frombuffer(data[offset:offset+size*8], dtype=np.float64)
        matrix.row = np.frombuffer(data[offset+size*8:offset+size*16], dtype=np.int32)
        matrix.col = np.frombuffer(data[offset+size*16:offset+size*20], dtype=np.int32)
        offset += size*20
        return offset
    
    def deserialize(self, data: bytes, offset: int) -> int:
        offset = self.deserialize_matrix(self.users, data, offset)
        offset = self.deserialize_matrix(self.items, data, offset)
        offset = self.deserialize_matrix(self.user_biases,
