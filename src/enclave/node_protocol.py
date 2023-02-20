from json_utils import split
from node_protocolfile import NodeProtocol
from tripletvector import TripletVector
from datastore import DataStore
from mf_node import MFNode
from hyper_mf_sgd import HyperMFSGD
from time_probe import TimeProbe

class EnclaveArguments:
    def __init__(self, degree, dpsgd, share_howmany, local, steps_per_iteration, epochs, userrank, train, train_size, test_size, nodes, modelshare, datashare):
        self.degree = degree
        self.dpsgd = dpsgd
        self.share_howmany = share_howmany
        self.local = local
        self.steps_per_iteration = steps_per_iteration
        self.epochs = epochs
        self.userrank = userrank
        self.train = train
        self.train_size = train_size
        self.test_size = test_size
        self.nodes = nodes
        self.modelshare = modelshare
        self.datashare = datashare

        self.rank_netid = {}
        self.netid_rank = {}

def ocall_farewell():
    pass

class NodeProtocol:
    def __init__(self):
        self.degree_ = -1

    def init(self, args):
        self.degree_ = args.degree
        self.dpsgd_ = args.dpsgd
        self.share_howmany_ = args.share_howmany
        self.local_ = args.local
        self.steps_per_iteration_ = args.steps_per_iteration
        self.epochs_ = args.epochs

        # Train and test data
        node_data = DataStore()
        begin = args.train.cast()
        end = begin + args.train_size
        for t in TripletVector(begin, end):
            node_data[(t.row(), t.col())] = t.value()
        begin = args.train.cast()
        end = begin + args.test_size
        test_set = TripletVector(begin, end)

        self.node_ = MFNode(args.userrank, node_data, test_set, args.modelshare, args.datashare, "")
        print("Hello enclave! I'm {}. Train: {}. Test: {}".format(args.userrank, len(node_data), len(test_set)))

        i = 0
        for n in split(args.nodes, " "):
            if not n:
                continue
            if n != "-":
                self.node_.add_neighbour(i)
                self.rank_netid[i] = n
                self.netid_rank[n] = i
            i += 1

        print_training_summary(self.trigger_training())
        return 0

    def print_training_summary(self, info):
        if not info.dummy():
            epoch = self.node_.finished_epoch()
            print("{};{};{};{};{};{};{};{}".format(epoch, self.absolutetime_.stop(), info.train_err, info.test_err, info.train_count, info.duration, info.bytes_out, info.bytes_in))
            if epoch >= self.epochs_:
                print(node_.summary())
                ocall_farewell()

    def trigger_training(self):
        init_bias = 1
        init_factor = sqrt(0.9)
        hyper = HyperMFSGD(10, 0.001, 0.1, init_bias, init_factor)
        self.absolutetime_ = TimeProbe()
        self.absolutetime_.start()
        print("epoch;timestamp;trainerr;testerr;traincount;duration;bytesout;bytesin")
        self.node_.init_training(self, hyper, DPSGD if self.dpsgd_ else RMW
