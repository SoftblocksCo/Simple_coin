import yaml
import struct
import logging
import hashlib
import merkletools

# Tx encoding/decoding
def encode_number(value):
    return struct.pack('>I', value)

def decode_number(raw):
    return int.from_bytes(raw, byteorder='big')

def read_conf():
    with open('conf.yaml') as ff:
        return yaml.load(ff)

def get_merkle_root(txns):
    mt = merkletools.MerkleTools(hash_type='SHA256')

    for tx in txns:
        mt.add_leaf(tx.hash)
    mt.make_tree()

    return mt.get_merkle_root()
