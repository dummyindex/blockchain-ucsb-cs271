from utils import *

def simple_test_hash():
    b = sha256_byte(sha256_str("1"), sha256_str("1"))
    assert is_last_byte_valid(b) == False
    t1, t2, nonce = "a b 20", "b c 10", bytes(20)
    assert is_valid_nonce(t1, t2, nonce) == False
    valid_nonce = find_valid_nonce(t1, t2)
    # print("valid nonce is ", valid_nonce)
    assert is_valid_nonce(t1, t2, valid_nonce)
    print("SIMPLE TEST1 PASSED")
    return True

simple_test_hash()
