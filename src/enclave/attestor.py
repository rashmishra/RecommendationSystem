import base64
import datetime
import random
import struct
import time

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from sgx_cryptoall import Crypto

class Attestor:
    def __init__(self):
        self.attestees_ = {}

    def get_key(self, id):
        if self.attestees_[id]['attested']:
            return self.attestees_[id]['shared_key']
        return []

    def new_challenge(self, id, challenge):
        response = self.get_quote(id, challenge)
        if response:
            return self.challenge_response_message(response)
        return ""

    def challenge_response(self, id, quote_b64):
        quote = base64.b64decode(quote_b64)
        peer_pubkey = []
        self.check_mrenclave_and_get_ecdhpeer(quote, peer_pubkey)
        qve_report_info = sgx_ql_qe_report_info_t()
        qve_report_info.app_enclave_target_info = sgx_target_info_t()
        status = sgx_self_target(qve_report_info.app_enclave_target_info)
        if status != 0:
            print("sgx_self_target: failed")
            return -3
        ret = -1
        rand_nonce = self.get_rand(len(qve_report_info.nonce.rand))
        struct.pack_into("16s", qve_report_info.nonce.rand, 0, *rand_nonce)
        expiration_check_date = c_int64()
        collateral_expiration_status = c_uint32()
        quote_verification_result = sgx_ql_qv_result_t()
        supplemental_data = create_string_buffer(1000)
        supplemental_data_size = c_uint32(supplemental_data._length_)
        ret = ocall_verify_quote(byref(ret), cast(quote, POINTER(c_uint8)), len(quote),
                                  byref(qve_report_info), byref(expiration_check_date),
                                  byref(collateral_expiration_status),
                                  byref(quote_verification_result), cast(supplemental_data, POINTER(c_uint8)),
                                  supplemental_data_size,
                                  byref(supplemental_data_size))
        if ret != 0:
            print("Quote could not be verified. Returned: ", ret)
            return -4
        if supplemental_data_size.value > len(supplemental_data):
            print("Supplemental data too big")
            return -5
        else:
            supplemental_data = supplemental_data[:supplemental_data_size.value]
        qve_isvsvn_threshold = 3
        ret_verify = sgx_tvl_verify_qve_report_and_identity(cast(quote, POINTER(c_uint8)), len(quote),
                                                            byref(qve_report_info),
                                                            expiration_check_date,
                                                            collateral_expiration_status,
                                                            quote_verification_result,
                                                            cast(supplemental_data, POINTER(c_uint8)),
                                                            supplemental_data_size.value, qve_isvsvn_threshold)
        if ret_verify != SGX_QL_SUCCESS:
            print("Could not verify report and/or identity of QE")
            return -6
        ret = self.quote_check_result(quote_verification_result)
        if ret >= 0:
            self.attestees_[id]['attested'] = True
            self.attestees_[id]['ecdh'].peer_pubkey(peer_pubkey)
            self.attestees_[id]['shared_key'] = self.attestees_[id]['ecdh'].derive_shared_key()
