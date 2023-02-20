import math
from typing import List, Dict, Tuple, Optional, Union
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
import random
import os
import time
from typing_extensions import Protocol


class TripletVector:
    def __init__(self, v: List[Tuple[int, int, float]]) -> None:
        self.v = v

    def get_triplets(self):
        return self.v


class ModelMergerType(Enum):
    RMW = 1
    DPSGD = 2


@dataclass
class TrainInfo:
    train_err: float
    train_count: int
    test_err: float
    duration: float
    bytes_out: int
    bytes_in: int


class DataStore:
    def __init__(self, d: Dict[str, Union[List[float], List[int]]]) -> None:
        self.d = d

    def get(self, k: str):
        return self.d[k]


class Communication(ABC):
    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def rank(self) -> int:
        pass

    @abstractmethod
    def send(self, dest: int, data: bytes) -> None:
        pass

    @abstractmethod
    def recv(self, source: int) -> Tuple[int, bytes]:
        pass


class ModelMerger(ABC):
    @abstractmethod
    def merge(self, epoch: int) -> None:
        pass

    @abstractmethod
    def share(self, epoch: int) -> int:
        pass

    @abstractmethod
    def receive(self, src: int, model: 'ShareableModel') -> None:
        pass

    @abstractmethod
    def received_all(self, epoch: int, degree: int) -> bool:
        pass


class MFSGDTrainer(ABC):
    @abstractmethod
    def train(self) -> Tuple[float, int]:
        pass

    @abstractmethod
    def test(self, test_set: TripletVector) -> float:
        pass

    @abstractmethod
    def make_compressed(self) -> None:
        pass


class MFNode:
    def __init__(self, node_index: int, node_data: DataStore,
                 test_set: TripletVector, modelshare: bool,
                 datashare: bool, outdir: str) -> None:
        self.node_index_ = node_index
        self.node_data_ = node_data
        self.test_set_ = test_set
        self.modelshare_ = modelshare
        self.datashare_ = datashare
        self.outdir_ = outdir
        self.bytes_reported_ = 0
        self.bytes_in_ = 0
        self.finished_epoch_ = -1
        if not self.modelshare_:
            self.datashare_ = True
        self.neighbours_ = set()

    def rank(self) -> int:
        return self.node_index_

    def add_neighbour(self, rank: int) -> bool:
        return self.neighbours_.add(rank)

    def init_training(self, comm: Communication, h: 'HyperMFSGD',
                      model: ModelMergerType, local: int,
                      steps_per_iteration: int,
                      share_howmany: int) -> None:
        self.trainer_ = MFSGDDecentralized(
            self.node_index_, self.node_data_, h, steps_per_iteration)
        self.local_iterations_ = local
        if model == ModelMergerType.RMW:
            self.decentralized_sharing_ = RandomModelWalkMerger
