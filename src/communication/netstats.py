import threading

bytes_in = 0
bytes_out = 0

def add_bytes_out(n):
    global bytes_out
    if n == 0:
        return
    # print(f"out +{n}")
    bytes_out += n

def add_bytes_in(n):
    global bytes_in
    if n == 0:
        return
    # print(f"in +{n}")
    bytes_in += n
