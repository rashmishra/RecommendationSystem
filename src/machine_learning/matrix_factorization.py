import numpy as np
from scipy.sparse import coo_matrix

class MatrixFactorizationModel:
    def __init__(self, rank):
        self.rank_ = rank
        self.weights_ = coo_matrix((rank, rank))
        self.weights_.users = coo_matrix((rank, rank))
        self.weights_.items = coo_matrix((rank, rank))
        self.weights_.user_biases = np.zeros((1, rank))
        self.weights_.item_biases = np.zeros((1, rank))

    def predict(self, user, item):
        return self.weights_[user, item]

    def rmse(self, testset):
        count = 0
        sumofsquares = 0
        for t in testset:
            diff = t.value - self.predict(t.row, t.col)
            sumofsquares += diff * diff
            count += 1
        return np.sqrt(sumofsquares / count)

    def init_item(self, item, column):
        if self.weights_.items.getcol(item) is None:
            self.find_space(0, item)
            self.weights_.items.getcol(item)[:] = column
            return True
        return False

    def init_user(self, user, column):
        if self.weights_.users.getcol(user) is None:
            self.find_space(user, 0)
            self.weights_.users.getcol(user)[:] = column
            return True
        return False

    def zero_embedding(self):
        return np.zeros((self.rank_, 1))

    def make_compressed(self):
        self.weights_.users = self.weights_.users.tocsr()
        self.weights_.items = self.weights_.items.tocsr()
        self.weights_.user_biases = self.weights_.user_biases.tocsr()
        self.weights_.item_biases = self.weights_.item_biases.tocsr()

    def item_merge_column(self, Y, Other):
        for item in range(Other.shape[1]):
            if self.init_item(item, Other.getcol(item)):
                continue
            Y.getcol(item)[:] = (Y.getcol(item) + Other.getcol(item)) / 2.

    def user_merge_column(self, X, Other):
        for user in range(Other.shape[1]):
            if self.init_user(user, Other.getcol(user)):
                continue
            X.getcol(user)[:] = (X.getcol(user) + Other.getcol(user)) / 2.

    def merge_average(self, m):
        self.item_merge_column(self.weights_.items, m.weights_.items)
        self.item_merge_column(self.weights_.item_biases, m.weights_.item_biases)

        self.user_merge_column(self.weights_.users, m.weights_.users)
        self.user_merge_column(self.weights_.user_biases, m.weights_.user_biases)

    def prep_toshare(self):
        self.init_user(self.rank_, self.weights_.users.getcol(0))
        self.weights_.users.getcol(self.rank_)[:] = self.weights_.users.getcol(0)
        self.weights_.users.getcol(0)[:] = np.zeros((self.rank_, 1))
        self.weights_.user_biases[0, self.rank_] = self.weights_.user_biases[0, 0]
        self.weights_.user_biases[0, 0] = 0

    def metropolis_hastings(self, my_degree, models, factors, biases, isusers):
        ret = set()
        for i in range(factors.shape[1]):
            index = i
            sum_weights = 0
            embedding = self.zero_embedding()
           
