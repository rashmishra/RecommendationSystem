import csv
from typing import List, Tuple
import numpy as np
from collections import defaultdict

def csvitem_tovector(v: List[Tuple[int, int, int]], item: List[str], 
                     dim: Tuple[int, int], limit: int, filter_divisor: int, filter_modulo: int) -> bool:
    try:
        t = (int(item[0]) - 1, int(item[1]) - 1, int(float(item[2]) * 2))
        if limit > 0:
            users.add(t[0])
            if len(users) > limit:
                return False
        if filter_modulo < 0 or filter_divisor == 0 or t[0] % filter_divisor == filter_modulo:
            dim = (max(dim[0], t[0] + 1), max(dim[1], t[1] + 1))
            v.append(t)
    except ValueError:
        print(f"Unable to convert <{item[0]}, {item[1]}, {item[2]}>")
        return False
    return True

def csv_ratings_triplet_vector(fname: str) -> List[Tuple[int, int, int]]:
    v = []
    dim = (0, 0)
    if not csv_parse(fname, lambda x: csvitem_tovector(v, x, dim, -1, 0, -1)):
        return []
    return v

class FileBuckets:
    def __init__(self):
        self.buckets = {}
        self.joiner = ","
        
    def closeall(self):
        for b in self.buckets:
            self.buckets[b].close()
        self.buckets.clear()
        
    def __del__(self):
        self.closeall()
        
def csvitem_touserbucket(item: List[str], fb: FileBuckets) -> bool:
    try:
        user = int(item[0]) - 1
        if user not in fb.buckets:
            fb.closeall()
            fb.buckets[user] = open(item[0] + ".csv", "w")
        fb.buckets[user].write(fb.joiner.join(item) + "\n")
    except ValueError:
        print(f"Unable to convert <{item[0]}, {item[1]}, {item[2]}>")
        return False
    return True

def csv_bucketize_byuser(fname: str) -> bool:
    filebuckets = FileBuckets()
    if not csv_parse(fname, lambda x: csvitem_touserbucket(x, filebuckets)):
        return False
    return True

def csv_ratings_sparse_matrix(fname: str) -> np.ndarray:
    v = csv_ratings_triplet_vector(fname)
    dim = (max(x[0] for x in v) + 1, max(x[1] for x in v) + 1)
    m = np.zeros(dim, dtype=np.uint8)
    for t in v:
        m[t[0], t[1]] = t[2]
    return m
