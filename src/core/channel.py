from src.core.router import Router


class Channel(object):
    def __init__(self, r1: Router, r2: Router, duplex, weight):
        self.duplex = duplex
        self.weight = weight
        self.r1 = r1
        self.r2 = r2
        pass

    def equals(self, r1, r2):
        return (self.r1.id == r1 and self.r2.id == r2) or (self.r1.id == r2 and self.r2.id == r1)