import random

def split_vectors(from_idx, to_idx, src, train, test):
    tmult = 0.7
    count = to_idx - from_idx
    tcount = int(tmult * count)
    indexes = set()
    while len(indexes) != tcount:
        indexes.add(from_idx + random.randint(0, count-1))
    for i in range(from_idx, to_idx):
        if i not in indexes:
            test.append(src[i])
        else:
            train.append(src[i])

def split_data(from_vec, train, test):
    i = 0
    id = -1
    count = 0
    idx = -1
    random.seed(0)
    for i in range(len(from_vec)):
        if id != from_vec[i].row:
            if id != -1:
                split_vectors(idx, i, from_vec, train, test)
            id = from_vec[i].row
            idx = i
    if idx != i - 1:
        split_vectors(idx, i, from_vec, train, test)
    assert len(from_vec) == len(train) + len(test)

def read_and_split(fname, train, test, limit=None, filter_divisor=None, filter_modulo=None):
    v = []
    dim = (0, 0)
    def csvitem_tovector(item):
        v.append(item)
    csv_parse(fname, csvitem_tovector, dim, limit, filter_divisor, filter_modulo)
    if v:
        from_vec = TripletVector(v)
        split_data(from_vec, train, test)
    return dim

def read_data(fname, m, test):
    train = []
    dim = read_and_split(fname, train, test)
    if dim[0] == 0 or dim[1] == 0:
        return False
    fill_matrix(m, dim, train)
    return True
