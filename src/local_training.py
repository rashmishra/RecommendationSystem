import argparse
import os
import pwd
from data_splitter import Ratings, read_data
from machine_learning.matrix_factorization import MFSGD, MatrixFactorizationModel
from matrices.matrix_serializer import JsonSerializer
from threads.thread_pool import ThreadPool
from typing import List, Tuple

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='MF local training: PoC to check implementation correctness')
    parser.add_argument('-f', '--filename', type=str, help='Data file')
    args = parser.parse_args()
    return args

def run(ratings: Ratings, test: List[Tuple[int, int, int]]) -> None:
    tp = ThreadPool()
    iters = [201]
    ranks = [10]
    lambdas = [0.1]
    etas = [0.005]
    results = []
    for iter in iters:
        for rank in ranks:
            for eta in etas:
                for lam in lambdas:
                    shared = MFSGD.trainX(ratings, 2, 10, rank, eta, lam, iter, test)
                    key = f'r={rank} n={eta} l={lam} i={iter}'
                    results.append((key, tp.submit(shared)))

    once = False
    for key, future in results:
        model = future.result()
        print(f'{key}: {model.rmse(test)}')
        """
        if not once:
            js = JsonSerializer()
            serial = js.serialize(model.item_features())
            print(serial.decode())
            once = True
        """

def main() -> None:
    args = parse_args()

    homedir = os.getenv('HOME')
    if homedir is None:
        homedir = pwd.getpwuid(os.getuid()).pw_dir

    fname = os.path.join(homedir, 'movielens/ml-latest-small/ratings.csv')
    if args.filename is None:
        print(f'Data file not provided. See option -f ($ {os.path.basename(__file__)} -?)\nTrying default: {fname}')

    else:
        fname = args.filename

    ratings, test = read_data(fname)

    run(ratings, test)

if __name__ == '__main__':
    main()
