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

def get_logger():
    logger = logging.getLogger('abci.app')

    if logger.hasHandlers():
        return logger

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
