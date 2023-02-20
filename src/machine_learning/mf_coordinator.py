from matrix_factorization import MatrixFactorization
from random import sample
from threading import Thread
from time import time

class Graph:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

    def out_edges(self, node):
        return [(node, neighbour) for neighbour in self.vertices if neighbour != node]

def random_graph_small_world(num_nodes):
    return Graph([i for i in range(num_nodes)], [])
    
def random_graph_erdos_renyi(num_nodes):
    num_edges = num_nodes * 0.05
    edges = set()
    while len(edges) < num_edges:
        src, dst = sample(range(num_nodes), 2)
        if src < dst:
            edges.add((src, dst))
        elif src > dst:
            edges.add((dst, src))
    return Graph([i for i in range(num_nodes)], list(edges))
    
class MFNode:
    def __init__(self, id, low_score, high_score, matrix_rank):
        self.id = id
        self.low_score = low_score
        self.high_score = high_score
        self.matrix_rank = matrix_rank
        self.neighbours = set()
        self.items = []
        self.model = None

    def add_neighbour(self, node_id):
        if node_id != self.id:
            self.neighbours.add(node_id)
            return True
        return False

    def init_training(self, coordinator, learning_rate, regularization, dpsgd):
        num_items = self.high_score - self.low_score + 1
        self.items = list(range(self.low_score, self.high_score + 1))
        self.model = MatrixFactorization(self.matrix_rank, num_items, num_items)
        self.model.init_model()
        self.coordinator = coordinator
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.dpsgd = dpsgd

    def train(self, epoch):
        train_items = self.items[:int(len(self.items)*0.9)]
        test_items = self.items[int(len(self.items)*0.9):]
        self.model.train(train_items, self.learning_rate, self.regularization, self.dpsgd)
        train_err = self.model.calc_error(train_items)
        test_err = self.model.calc_error(test_items)
        self.share(epoch)
        return train_err, len(train_items), test_err

    def share(self, epoch):
        model_data = self.model.get_model_data()
        for n in self.neighbours:
            self.coordinator.send(self.id, n, model_data)

    def receive(self, sender_id, data):
        self.model.set_model_data(data)
    
class MFCoordinator:
    def __init__(self, nodes, shared_memory):
        self.nodes = nodes
        self.shared_memory = shared_memory
        self.node_models = {}

    def establish_relations(self, graph):
        edges = 0
        for node in graph.vertices:
            for edge in graph.out_edges(node):
                src, dst = edge
                if src < len(self.nodes) and dst < len(self.nodes):
                    if self.nodes[src].add_neighbour(dst):
                        edges += 1
                    if self.nodes[dst].add_neighbour(src):
                        edges += 1
                else:
                    print(f"Out of bounds nodes[{src}].add_neighbour({dst
