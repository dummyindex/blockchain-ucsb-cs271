import hashlib
import os

def sha256_str(s):
    return hashlib.sha256(s.encode('utf-8')).digest()

def sha256_byte(b1, b2=None):
    assert b1 != None
    if b2:
        b1 += b2
    return hashlib.sha256(b1).digest()


def is_last_byte_valid(hash_val):
    '''
    input : 32 bytes hash returned by sha256
    output : name
    '''
    assert len(hash_val) == 32
    last = hash_val[-1]
    res = last == ord('0') or last == ord('1') or last == ord('2')
    return res

def gen_nonce(nonce_len=32):
    return os.urandom(nonce_len)

def is_valid_nonce(t1, t2, nonce):
    '''
    t1, t2, nonce: str, str and byte nonce
    '''
    temp = sha256_byte(sha256_str(t1) + sha256_str(t2))
    hash_final = sha256_byte(temp + nonce)
    return is_last_byte_valid(hash_final)

def find_valid_nonce(t1, t2):
    nonce = gen_nonce()
    while not is_valid_nonce(t1, t2, nonce):
        nonce = gen_nonce()
    return nonce
