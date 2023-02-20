from machine_learning.mf_node import MFNode
from typing import List, Tuple
from args_rex import EnclaveArguments

class NodeProtocol:
    def __init__(self):
        self.node_ = None
        self.degree_ = 0
        self.steps_per_iteration_ = 0
        self.share_howmany_ = 0
        self.local_ = 0
        self.epochs_ = 0
        self.dpsgd_ = False
        self.absolutetime_ = None
        self.waiting = {}
        self.neighbors = set()
        self.attested = {}
        self.rank_netid = {}
        self.netid_rank = {}
    
    def init(self, args: EnclaveArguments) -> int:
        self.node_ = MFNode(args.get_model_config())
        self.degree_ = args.degree
        self.steps_per_iteration_ = args.steps_per_iteration
        self.share_howmany_ = args.share_howmany
        self.local_ = args.local
        self.epochs_ = args.epochs
        self.dpsgd_ = args.dpsgd
        self.absolutetime_ = args.absolutetime
        return 0
    
    def input(self, message: List[str]) -> None:
        # do something with input message
    
    def send(self, src: int, dst: int, m: ShareableModel) -> int:
        # do something to send the ShareableModel from src to dst
        return 0
    
    def print_training_summary(self, info: TrainInfo) -> None:
        # do something to print the training summary
        
    def trigger_training(self) -> TrainInfo:
        # do something to trigger training
        return TrainInfo()
    
    def all_neighbors_attested(self) -> bool:
        # check if all neighbors have been attested
        return False
    
    def send_data(self, dst: str, data: str) -> int:
        # do something to send data to dst
        return 0
    
    def send_queued(self, dstid: str) -> int:
        # do something to send queued data to dstid
        return 0
    
    def encrypted_send(self, dst: str, data: str) -> int:
        # do something to send encrypted data to dst
        return 0
    
    def decrypt_received(self, src: str, data: str) -> Tuple[bool, List[int]]:
        # do something to decrypt received data from src
        return (False, [])
    
    # the following methods are only included if not running in a "native" environment
    def trigger_attestation(self, nodeid: str) -> None:
        pass
    
    def new_attest_msg(self, dst: str) -> str:
        return ""
    
    def attestation_message(self, nodeid: str, message: str) -> None:
        pass
