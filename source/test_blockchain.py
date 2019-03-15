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

if __name__ == "__main__":
    test1()
