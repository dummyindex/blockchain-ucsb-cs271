from utils import *

class Block:
    def __init__(self, ta, tb, term, prev_header_hash):
        self.ta = ta
        self.tb = tb
        self.term = term
        self.prev_header_hash = prev_header_hash
        self.transation_hash = sha256_byte(sha256_str(ta) + sha256_str(tb))
        self.nonce = find_valid_nonce(ta, tb)

    def hash(self):
        val = sha256_str(str(self.term) + self.prev_header_hash.hex()
                         + self.transation_hash.hex() + self.nonce.hex())
        return val

    def create_dummy_block():
        return Block("", "", 0, bytes(0))

    def __str__(self):
        return "term: %d, ta: %s, tb: %s, prev_hash: %s" % (self.term, self.ta, self.tb, self.prev_header_hash.hex())


class BlockChain():
    def __init__(self):
        self.chain = [Block.create_dummy_block()]

    def append(self, block):
        self.chain.append(block)

    def get(self, idx):
        return self.chain[idx]

    def pop(self, idx):
        self.chain.pop(idx)


    def __len__(self):
        return len(self.chain)
