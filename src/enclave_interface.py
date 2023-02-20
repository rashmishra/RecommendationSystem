from typing import List

class EnclaveArguments:
def init(self, input_file: str, output_file: str, k: int, m: int):
self.input_file = input_file
self.output_file = output_file
self.k = k
self.m = m

class EnclaveInterface:
g_eid = None

@staticmethod
def init(args: EnclaveArguments) -> bool:
    ret = None
    if NATIVE:
        ret = ecall_init(args)
    else:
        if initialize_enclave(EnclaveInterface.g_eid, "enclave_rex.signed.so", "enclave_rex.token"):
            return False
        ret = ecall_init(EnclaveInterface.g_eid, ret, args)

    if ret:
        print("Failed to init enclave")
        exit(2)
    return True

@staticmethod
def finish() -> None:
    if NATIVE:
        # ecall_finish();
        pass
    else:
        # ecall_finish(g_eid);
        destroy_enclave(EnclaveInterface.g_eid)
