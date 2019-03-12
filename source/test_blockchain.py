from Block import *
from utils import *

def test1():
    ta = "a b 10"
    tb = "c a 20"
    b0 = Block.create_dummy_block()
    term = 0
    b1 = Block(ta, tb, term, b0.hash())
    print(b1)
    assert b1.prev_header_hash == b0.hash()
    print("SIMPLE BLOCKCHAIN TEST1 PASSED")

if __name__ == "__main__":
    test1()
