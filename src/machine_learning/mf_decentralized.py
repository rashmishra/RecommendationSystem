from typing import List, Dict, Tuple
from random import randint, sample
from collections import defaultdict
import numpy as np


class HyperMFSGD:
    def __init__(self, num_factors: int, init_stdev: float, reg: float, learn_rate: float, init_mean: float = 0.0):
        self.num_factors = num_factors
        self.init_stdev = init_stdev
        self.reg = reg
        self.learn_rate = learn_rate
        self.init_mean = init_mean
        self.init_column_ = np.random.normal(self.init_mean, self.init_stdev, self.num_factors)
        self.init_bias = 0.0

        
class MatrixFactorizationModel:
    def __init__(self, num_users: int, num_items: int, num_factors: int, init_stdev: float):
        self.num_users = num_users
        self.num_items = num_items
        self.num_factors = num_factors
        self.init_stdev = init_stdev
        self.user_vectors = np.random.normal(0, self.init_stdev, (self.num_users, self.num_factors))
        self.item_vectors = np.random.normal(0, self.init_stdev, (self.num_items, self.num_factors))
        self.user_biases = np.zeros(self.num_users)
        self.item_biases = np.zeros(self.num_items)
        self.global_bias = 0.0
        self.compressed = False
        
    def make_compressed(self):
        self.global_bias = 0.0
        self.user_biases = self.user_biases - np.mean(self.user_biases)
        self.item_biases = self.item_biases - np.mean(self.item_biases)
        self.global_bias = np.mean(self.user_biases) + np.mean(self.item_biases)
        self.user_biases -= self.global_bias
        self.item_biases -= self.global_bias
        self.compressed = True

    def find_space(self, user: int, item: int, init_column: np.ndarray, init_bias: float):
        if self.compressed:
            self.global_bias = 0.0
            self.user_biases = self.user_biases - np.mean(self.user_biases)
            self.item_biases = self.item_biases - np.mean(self.item_biases)
            self.global_bias = np.mean(self.user_biases) + np.mean(self.item_biases)
            self.user_biases -= self.global_bias
            self.item_biases -= self.global_bias
            self.compressed = False
            
        self.user_vectors[user] = init_column
        self.item_vectors[item] = init_column
        self.user_biases[user] = init_bias
        self.item_biases[item] = init_bias
        self.global_bias = (np.mean(self.user_biases) + np.mean(self.item_biases)) / 2

    def init_user(self, user: int, init_column: np.ndarray):
        if self.compressed:
            self.global_bias = 0.0
            self.user_biases = self.user_biases - np.mean(self.user_biases)
            self.item_biases = self.item_biases - np.mean(self.item_biases)
            self.global_bias = np.mean(self.user_biases) + np.mean(self.item_biases)
            self.user_biases -= self.global_bias
            self.item_biases -= self.global_bias
            self.compressed = False
            
        self.user_vectors[user] = init_column
        self.user_biases[user] = 0.0

    def init_item(self, item: int, init_column: np.ndarray):
        if self.compressed
