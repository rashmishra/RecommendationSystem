import communication.sync_zmq as CommunicationZmq
import os
import ctypes
import struct
import sys
import threading
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives import serialization, hashes

mutex = threading.Lock()

BLD = "\x1B[1m"
RED = "\x1B[31m"
GRN = "\x1B[32m"
YEL = "\x1B[33m"
BLU = "\x1B[34m"
MAG = "\x1B[35m"
CYN = "\x1B[36m"
WHT = "\x1B[37m"
RST = "\x1B[0m"

def uprint(str):
    mutex.acquire()
    print(YEL + str + RST, end="")
    sys.stdout.flush()
    mutex.release()

def ocall_send(id, buffer, length):
    return CommunicationZmq.send(id, buffer, length)

def ctrlc_handler(signal, frame):
    print("User interrupt, quitting")
    os._exit(0)

def ocall_farewell():
    ctrlc_handler(None, None)

class TargetInfo:
    def __init__(self):
        self.done = False
        self.qe_target_info = None

target = TargetInfo()

def qe3_error(func, qe3_ret):
    error, extra = None, None
    retrieve_error_msg(qe3_ret, error, extra)
    print(func + ": " + error + " " + extra)

def ocall_get_target_info(p_qe3_target):
    global target
    qe3_ret = None
    if not target.done:
        qe3_ret = sgx_qe_get_target_info(ctypes.byref(target.qe_target_info))
        if SGX_QL_SUCCESS != qe3_ret:
            qe3_error("sgx_qe_get_target_info", qe3_ret)
            return -1
        else:
            target.done = True
    ctypes.memmove(p_qe3_target, ctypes.byref(target.qe_target_info),
                   ctypes.sizeof(sgx_target_info_t))
    return 0

def ocall_get_quote(report, quote_buff, buff_size):
    quote_size = ctypes.c_uint32(0)
    qe3_ret = sgx_qe_get_quote_size(ctypes.byref(quote_size))
    if SGX_QL_SUCCESS != qe3_ret:
        qe3_error("in sgx_qe_get_quote_size", qe3_ret)
        return -1

    if buff_size < quote_size.value:
        print("Quote (" + str(quote_size.value) + "B) doesn't fit in the buffer provided (" + str(buff_size) + "B)")
        return -2

    quote_buff_raw = (ctypes.c_uint8 * buff_size)()
    ctypes.memset(quote_buff_raw, 0, buff_size)

    # Get the Quote
    qe3_ret = sgx_qe_get_quote(report, quote_size.value, ctypes.byref(quote_buff_raw))
    if SGX_QL_SUCCESS != qe3_ret:
        qe3_error("sgx_qe_get_quote", qe3_ret)
        return -3

    ctypes.memmove(quote_buff, quote_buff_raw, quote_size.value)
    return quote_size.value

def ocall_verify_quote(quote_data, quote_size, qve_report_info, current_time, collateral_expiration_status, quote_verification_result, supplemental_data, buff_size, supplemental
