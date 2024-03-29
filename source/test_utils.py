from utils import *

def simple_test_hash():
    b = sha256_byte(sha256_str("1"), sha256_str("1")) 
    assert is_last_byte_valid(b) == False
    t1, t2, nonce = "a b 20", "b c 10", bytes(20)
    assert is_valid_nonce(t1, t2, nonce) == False
    valid_nonce = find_valid_nonce(t1, t2)
    # print("valid nonce is ", valid_nonce)
    assert is_valid_nonce(t1, t2, valid_nonce)
    # print(valid_nonce.hex())
    print("SIMPLE TEST1 PASSED")
    return True

def test_hash_encode_decode():
    b = sha256_byte(sha256_str("21"), sha256_str("afqwfyubgfv2yi4t1"))
    assert decode_bytes(encode_bytes(b)) == b
    print("TEST HASH DECODE ENCODE CONSISTENCY PASSED")
    
simple_test_hash()
test_hash_encode_decode()
