from Block import *
from utils import *
import random
def test1():
    ta = "a b 10"
    tb = "c a 20"
    b0 = Block.create_dummy_block()
    term = 0
    b1 = Block(ta, tb, term, b0.hash())
    print(b1)
    assert b1.prev_header_hash == b0.hash()
    print(b1.to_dict())
    chain = BlockChain()

    l = random.randint(10, 100)
    for i in range(l):
        chain.append(b1)

    # check length
    for i in range(1, len(chain)):
        l1 = len(chain.get_entries_start_at_list(i-1))
        l2 = len(chain.get_entries_start_at_list(i))
        assert (l1 - 1) == l2
    print("SIMPLE BLOCKCHAIN TEST1 PASSED")

def test_block_json():
    ta = "a b 10"
    tb = "c a 20"
    b0 = Block.create_dummy_block()
    term = 0
    b1 = Block(ta, tb, term, b0.hash())
    b2 = Block.from_dict(b1.to_dict())

    assert b1.ta == b2.ta
    assert b1.tb == b2.tb
    assert b1.term == b2.term
    assert b1.prev_header_hash == b2.prev_header_hash
    assert b1.txn_hash == b2.txn_hash
    assert b1.nonce == b2.nonce
    assert b1.final_hash == b2.final_hash
    print("BLOCK JSON COMPRESS/DECOMPRESS PASSSES")
    
if __name__ == "__main__":
    test1()
    test_block_json()
