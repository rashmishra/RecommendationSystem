from typing import List, Tuple
from scipy.sparse import csr_matrix
import numpy as np

class HyperMFSGD:
    def __init__(self, matrix_rank: int, learning: float, regularization: float,
                 init_bias: float, init_factor: float):
        self.matrix_rank = matrix_rank
        self.learning = learning
        self.regularization = regularization
        self.init_bias = init_bias
        self.init_factor = init_factor

class MFSGD:
    def __init__(self, hyper: HyperMFSGD):
        self.hyper = hyper
        self.model = None

    def train(self, user: int, item: int, score: float) -> float:
        error = score - self.predict(user, item)
        bu = self.model.user_bias(user)
        bi = self.model.item_bias(item)
        uf = self.model.user_factor(user)
        vf = self.model.item_factor(item)
        self.model.update_user_bias(user, bu + self.hyper.learning * (error - self.hyper.regularization * bu))
        self.model.update_item_bias(item, bi + self.hyper.learning * (error - self.hyper.regularization * bi))
        self.model.update_user_factor(user, uf + self.hyper.learning * (error * vf - self.hyper.regularization * uf))
        self.model.update_item_factor(item, vf + self.hyper.learning * (error * uf - self.hyper.regularization * vf))
        return error ** 2

    def predict(self, user: int, item: int) -> float:
        return self.model.predict(user, item)

class MFSGDCentralized(MFSGD):
    def __init__(self, ratings: csr_matrix, hyper: HyperMFSGD):
        super().__init__(hyper)
        self.ratings = ratings
        self.user_locks = {}
        self.item_locks = {}

    def get_user_lock(self, user: int) -> threading.Lock:
        with usermtx:
            if user not in self.user_locks:
                self.user_locks[user] = threading.Lock()
            return self.user_locks[user]

    def get_item_lock(self, item: int) -> threading.Lock:
        with itemmtx:
            if item not in self.item_locks:
                self.item_locks[item] = threading.Lock()
            return self.item_locks[item]

    def parallel_train(self, it: csr_matrix, item: int) -> Tuple[float, int]:
        err = 0
        count = 0
        with self.get_item_lock(item):
            for user, score in zip(it.indices, it.data):
                with self.get_user_lock(user):
                    err += self.train(user, item, score)
                    count += 1
        return err, count

    def init(self):
        def init_func(it):
            user = it.row
            item = it.col
            self.model.find_space(user, item, self.hyper.init_column_, self.hyper.init_bias)
            self.model.init_item(item, self.hyper.init_column_)
            self.model.init_user(user, self.hyper.init_column_)
        self.ratings = self.ratings.tocoo()
        for it in zip(self.ratings.row, self.ratings.col, self.ratings.data):
            init_func(it)

    def train(self) -> Tuple[float, int]:
        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            results = [executor.submit(self.parallel_train, self.ratings.getcol(item), item)
                       for item in range(self.ratings.shape[1])]
            total_err = 0
            count
