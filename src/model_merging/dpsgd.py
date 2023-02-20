from dpsgd import DPSGDModelPtr, DPSGDShareableModel
from model_merger import ModelMerger
from matrix_factorization_model import MatrixFactorizationModel
from communication import Communication
from typing import Set
from sharing_ratings import SharingRatings
from mf_sgd_decentralized import MFSGDDecentralized
from dpsgd_entry import DPSGDEntry
from shareable_model import ShareableModel
import std

class DPSGDMerger(ModelMerger):
    def __init__(self, rank: int, share_howmany: int, c: Communication, trainer: MFSGDDecentralized, neighbours: Set[int], modelshare: bool, datashare: bool):
        super().__init__(rank, share_howmany, c, trainer, neighbours, modelshare, datashare)

    def share(self, epoch: int) -> int:
        rawdata = SharingRatings()
        if self.datashare:
            rawdata = self.extract_ratings(self.share_howmany)

        toshare = DPSGDModelPtr()
        if self.modelshare:
            toshare = DPSGDShareableModel(epoch, self.trainer.model(), rawdata, len(self.neighbours))
        else:
            toshare = DPSGDShareableModel(epoch, MatrixFactorizationModel(-2), rawdata, len(self.neighbours))

        ret = 0
        for peer in self.neighbours:
            ret += self.communication.send(self.userrank, peer, toshare)

        return ret

    def merge(self, epoch: int):
        with std.unique_lock(std.mutex()):
            models = []
            count = 0
            for m in self.received_models[epoch]:
                src = m[0]
                shared = m[1]
                model = DPSGDShareableModel.cast(shared)
                models.append(DPSGDEntry(src, model.degree_, shared.epoch, shared.model_))
                count += self.trainer.add_raw_ratings(model.rawdata)
                self.recvdfrom.discard((src, shared.epoch))

            if len(self.neighbours) != len(models):
                std.cerr << f"oh no! I am {self.userrank}. I have {len(self.neighbours)} neighbours: but received {len(models)} models." << std.end
                for n in self.neighbours:
                    std.cerr << n << " "
                std.cerr << std.end
                for m in models:
                    std.cerr << f"{m.src}({m.epoch}) "
                std.cerr << std.end

                std.abort()

            if self.modelshare:
                local_model = self.trainer.mutable_model()
                local_model.merge_weighted(len(self.neighbours), models)

            self.received_models[epoch].clear()

class DPSGDShareableModel(ShareableModel):
    def __init__(self, e: int, m: MatrixFactorizationModel, data: SharingRatings, degree: int):
        super().__init__(e, "DPSGD", m, data)
        self.degree = degree

    def serialize(self) -> List[int]:
        ret = super().serialize()
        dptr = bytes(self.degree)
        ret.extend(dptr)
        return ret

    def deserialize(self, data: List[int]) -> int:
        offset = super().deserialize(data)
        assert offset < len(data) and len(data) - offset >= self.degree
        self.degree = int.from_bytes(bytes(data[offset:offset + sizeof(self.degree)]), byteorder='little')
        assert self.degree != 0
        return offset + sizeof(self.degree)
