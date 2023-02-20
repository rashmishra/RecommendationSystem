from typing import List, Tuple
import json

class MatrixSerializer:
    def serialize(self, dense) -> List[int]:
        pass

    def serialize(self, sparse) -> List[int]:
        pass

    def deserialize_dense(self, data: List[int]):
        pass

    def deserialize_sparse(self, data: List[int]):
        pass


class JsonSerializer(MatrixSerializer):
    def serialize(self, dense) -> List[int]:
        return []

    def serialize(self, sparse) -> List[int]:
        matrix = {}
        column = []
        for i in range(sparse.outerSize()):
            for j in range(sparse.innerIndexPtr()[i], sparse.innerIndexPtr()[i + 1]):
                line = {}
                line[str(sparse.innerIndex()[j])] = sparse.value()[j]
                column.append(line)
            if column:
                matrix[str(i)] = column
                column = []

        m = json.dumps(matrix)
        return [ord(c) for c in m]

    def deserialize_dense(self, data: List[int]):
        return []

    def deserialize_sparse(self, data: List[int]):
        return []

class BinarySerializer(MatrixSerializer):
    def serialize(self, dense) -> List[int]:
        return []

    def serialize(self, sparse) -> List[int]:
        triplets = []
        for i in range(sparse.outerSize()):
            for j in range(sparse.innerIndexPtr()[i], sparse.innerIndexPtr()[i + 1]):
                triplets.append((i, sparse.innerIndex()[j], sparse.value()[j]))

        ret = []
        for t in triplets:
            ret.append(t[0])
            ret.append(t[1])
            ret.append(t[2])

        return ret

    def deserialize_dense(self, data: List[int]):
        return []

    def deserialize_sparse(self, data: List[int]):
        triplets = []
        for i in range(0, len(data), 3):
            triplets.append((data[i], data[i+1], data[i+2]))

        return self._triplets_to_matrix(triplets)

    def _triplets_to_matrix(self, triplets: List[Tuple[int, int, float]]) -> scipy.sparse.csr_matrix:
        from scipy.sparse import coo_matrix, csr_matrix
        coo = coo_matrix((len(triplets), 1))
        coo.data = [t[2] for t in triplets]
        coo.row = [t[0] for t in triplets]
        coo.col = [t[1] for t in triplets]

        return csr_matrix(coo)
