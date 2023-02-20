import argparse
import os
import pwd
import sys
import time
import numpy as np
import pandas as pd
import tensorflow as tf

from data_splitter import read_and_split
from machine_learning.mf_coordinator import MFNode
from pathlib import Path

DEFAULT_DIR = 'out'

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Read the data
    nodes = []
    read_data(args.input_fname, nodes, args.num_nodes, args.modelshare, args.datashare, args.capusers, args.output_dir)

    # Train the model
    coordinator = MFCoordinator(nodes, args.num_nodes, args.steps_per_iteration, args.embedding_size, args.dpsgd, args.randgraph, args.shared_memory)
    coordinator.run(args.local, args.epochs, args.share_howmany)

def read_data(fname, nodes, num_nodes, modelshare, datashare, cap, outdir):
    # Read and split the data
    train, test, dim = read_and_split(fname, cap=cap)

    # Calculate number of users per node
    num_users_per_node = dim[0] // num_nodes
    remaining_users = dim[0] % num_nodes
    users_per_node = [num_users_per_node] * num_nodes
    for i in range(remaining_users):
        users_per_node[i] += 1

    train_count = 0
    test_count = 0

    i = 0
    j = 0
    node_index = 0

    while node_index < num_nodes:
        # Create training data for this node
        num_users = users_per_node[node_index]
        ratings = np.zeros((num_users, dim[1]), dtype=np.uint8)
        while i < train.shape[0] and num_users > 0:
            if train[i][0] < (node_index+1)*num_users_per_node:
                user = train[i][0] - node_index*num_users_per_node
                item = train[i][1]
                rating = train[i][2]
                ratings[user][item] = rating
                i += 1
                num_users -= 1
            else:
                break

        # Create testing data for this node
        num_users = users_per_node[node_index]
        test_ratings = np.zeros((num_users, dim[1]), dtype=np.uint8)
        while j < test.shape[0] and num_users > 0:
            if test[j][0] < (node_index+1)*num_users_per_node:
                user = test[j][0] - node_index*num_users_per_node
                item = test[j][1]
                rating = test[j][2]
                test_ratings[user][item] = rating
                j += 1
                num_users -= 1
            else:
                break

        # Create the node object
        node = MFNode(ratings, test_ratings, modelshare, datashare, node_index, outdir)
        nodes.append(node)

        node_index += 1

def parse_args():
    parser = argparse.ArgumentParser(description='MF decentralized training: PoC to check implementation correctness')
    parser.add_argument('input_fname', help='Input data file')
    parser.add_argument('-s', '--sharedata
