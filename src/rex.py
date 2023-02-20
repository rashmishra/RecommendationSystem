import argp
import args_rex
import communication_manager
import data_splitter
import enclave_interface
import generic_utils
import pwd
import stringtools
import sync_zmq
import signal
import os
import sys
import threading
from typing import List, Tuple, Set

DEFAULT_PORT = 4444


class Arguments:
    def __init__(self) -> None:
        self.port = DEFAULT_PORT
        self.modelshare = True
        self.datashare = False
        self.dpsgd = False
        self.share_howmany = 20
        self.local = 1
        self.steps_per_iteration = 30
        self.epochs = 10
        self.capusers = 0
        self.input_fname = ""
        self.machines = ""


def parse_opt(key: int, arg: str, state: argp.argp_state) -> int:
    args = state.input  # type: Arguments
    if key == 'f':
        args.input_fname = arg
    elif key == 's':
        args.datashare = True
    elif key == 'x':
        args.modelshare = False
    elif key == 'h':
        args.share_howmany = int(arg)
    elif key == 'u':
        args.steps_per_iteration = int(arg)
    elif key == 'l':
        args.local = int(arg)
    elif key == 'd':
        args.dpsgd = True
    elif key == 'p':
        args.port = int(arg)
    elif key == 'e':
        args.epochs = int(arg)
    elif key == 'c':
        args.capusers = int(arg)
    elif key == 'm':
        args.machines = arg
    else:
        return argp.ARGP_ERR_UNKNOWN
    return 0


def farewell_message(s: int) -> int:
    unit = ''
    amount = generic_utils.bytes_human(NetStats.bytes_in, unit)
    print(f"\nData in: {amount} {unit}")
    amount = generic_utils.bytes_human(NetStats.bytes_out, unit)
    print(f"Data out: {amount} {unit}")
    print(f"\n({s}) bye!")
    return s


def find_userrank_and_neigh(machines: str, port: int) -> Tuple[int, int, Set[Tuple[str, int]], str]:
    hostname = os.uname().nodename

    hosts = machines.split(' ')
    index = 0
    myindex = -1
    neigh = set()
    nlist = ''
    for h in hosts:
        hostport = h.split(':')
        try:
            if myindex < 0 and hostname == hostport[0] and (len(hostport) == 1 and port == DEFAULT_PORT or len(hostport) > 1 and port == int(hostport[1])):
                myindex = index
            if len(hostport) > 1:
                neigh.add((hostport[0], int(hostport[1])))
            else:
                neigh.add((hostport[0], DEFAULT_PORT))
            nlist += h + ' '
        except:
            pass
        index += 1

    return myindex, len(hosts), neigh, nlist


def ctrlc_handler(s: int) -> None:
    if headsman_thread is None:
        enclave_interface.finish()
        headsman_thread = threading.Thread(target=lambda: communication_manager.CommunicationManager[communication_zmq].finish())
        headsman_thread.start()


def main() -> None:
    signal.signal(signal.SIGINT, ctrlc_handler)
