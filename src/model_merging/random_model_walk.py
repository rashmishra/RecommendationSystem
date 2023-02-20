import random

class RandomModelWalkMerger(ModelMerger):
    def __init__(self, rank, share_howmany, communication, trainer, neighbours, modelshare, datashare):
        super().__init__(rank, share_howmany, communication, trainer, neighbours, modelshare, datashare)

    def share(self, epoch):
        if self.datashare:
            rawdata = self.extract_ratings(self.share_howmany)
        else:
            rawdata = SharingRatings()

        toshare = ShareableModel(epoch, RMW, self.trainer.model() if self.modelshare else MatrixFactorizationModel(-2), rawdata)
        dummy = ShareableModel(epoch, RMW, MatrixFactorizationModel(-1), SharingRatings())

        peer = random.choice(list(self.neighbours))
        i = 0
        ret = 0
        for n in self.neighbours:
            if i == peer:
                ret += self.communication.send(self.userrank, n, toshare)
            else:
                ret += self.communication.send(self.userrank, n, dummy)
            i += 1

        return ret

    def merge(self, epoch):
        with self.recv_mtx:
            count = 0
            for model in self.received_models[epoch]:
                src, shared = model
                if shared.model.rank() != -1:
                    if self.modelshare:
                        self.trainer.mutable_model().merge_average(shared.model)
                    count += self.trainer.add_raw_ratings(shared.rawdata)
                self.recvdfrom.remove((src, shared.epoch))

            self.received_models[epoch].clear()
