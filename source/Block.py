from utils import *


class Block:
    def __init__(self, ta, tb, term, prev_header_hash, nonce=None):
        self.ta = ta
        self.tb = tb
        self.term = term
        self.prev_header_hash = prev_header_hash
        self.txn_hash = sha256_byte(sha256_str(ta) + sha256_str(tb))
        self.nonce = nonce
        if nonce == None:
            self.nonce = find_valid_nonce(ta, tb)
        self.final_hash = sha256_byte(self.txn_hash + self.nonce)

    def hash(self):
        val = sha256_str(str(self.term) + self.prev_header_hash.hex()
                         + self.txn_hash.hex() + self.nonce.hex())
        return val

    def create_dummy_block():
        return Block("", "", 0, bytes(0))

    def __str__(self):
        return "term: %d, ta: %s, tb: %s, prev_hash: %s" % (self.term, self.ta, self.tb, self.prev_header_hash.hex())


    def to_dict(self):
        return {
            "txns": [self.ta, self.tb],
            "nonce": encode_bytes(self.nonce),
            "term" : self.term,
            "prev_header_hash": encode_bytes(self.prev_header_hash),
            "txn_hash": encode_bytes(self.txn_hash),
            "final_hash": encode_bytes(self.final_hash)
        }

    def from_dict(d):
        ta = d["txns"][0]
        tb = d["txns"][1]
        nonce = decode_bytes(d["nonce"])
        term = d["term"]
        prev_header_hash = decode_bytes(d["prev_header_hash"])
        return Block(ta, tb, term, prev_header_hash, nonce)

class BlockChain():
    def __init__(self):
        self.chain = [Block.create_dummy_block()]
        self.commitIndex = 0

    def append(self, block):
        self.chain.append(block)

    def get(self, idx):
        return self.chain[idx]

    def pop(self, idx):
        self.chain.pop(idx)


    def __len__(self):
        return len(self.chain)

    def get_commitIndex(self):
        return self.commitIndex

    def get_entries_start_at_list(self, pos):
        res = []
        for i in range(pos, len(self.chain)):
            block = self.chain[i]
            res.append(block.to_dict())
        return res

    def lastLogIndex(self):
        return len(self.chain) - 1

    def lastLogTerm(self):
        return self.chain[-1].term

    def update_chain_at(self, start, block_list):
        # no need to calculate previous block's hash again
        self.chain = self.chain[:start]
        for i in range(start, len(self.chain)):
            self.chain.append(block_list[i - start])
            
