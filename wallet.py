from argparse import ArgumentParser
from time import time
from json import dumps
from binascii import hexlify
from binascii import unhexlify

from os import urandom
from os.path import isfile

from sys import exit
from sys import argv

import ed25519
import requests

parser = ArgumentParser("Simple wallet for SimpleCoin")
parser.add_argument('-n', '--new', help="Create new keypair", action="store_true")
parser.add_argument('-w', '--wallet', help="Path to the .sc wallet", default="my.sc")
parser.add_argument('-t', '--transaction', help="Create & sign a txn", action="store_true")

# Arguments for working with Tendermint
parser.add_argument('-b', '--broadcast', help="Broadcast txn to the network", default="")
parser.add_argument('-g', '--get_balance', help="Get balance for some address", default="")

# Arguments for message signing
parser.add_argument('-s', '--sign', help="Sign a message", action="store_true")
parser.add_argument('-c', '--check_sign', help="Specify the signature", default="")
parser.add_argument('-m', '--message', help="Message to sign or to check",
    required='-s' in argv or '--sign' in argv or '-c' in argv or '--check_sign' in argv, default=""
)
parser.add_argument('-p', '--pub_key', help="Public key, corresponding to the signature",
    required='-c' in argv or '--check_sign' in argv, default=""
)

# Arguments for creating new txn
parser.add_argument('-a', '--amount', help="Amount of coins to send in txn",
    required='-t' in argv or '--transaction' in argv, type=int
)
parser.add_argument('-r', '--receiver', help="Transaction receiver",
    required='-t' in argv or '--transaction' in argv,  type=str
)
parser.add_argument('-d', '--data', help="Small piece of data to store in txn",
    type=str, default=""
)

def read_signing_key(path):
    with open(path, "rb") as ff:
        keydata = ff.read().splitlines()[0]
    return ed25519.SigningKey(keydata, encoding="base64")

def read_verifying_key(path):
    with open(path, "rb") as ff:
        keydata = ff.read().splitlines()[1]
    return ed25519.VerifyingKey(keydata, encoding="base64")

if __name__ == "__main__":
    options = parser.parse_args()

    #  _ __   _____      __ __      ____ _| | | ___| |_
    # | '_ \ / _ \ \ /\ / / \ \ /\ / / _` | | |/ _ \ __|
    # | | | |  __/\ V  V /   \ V  V / (_| | | |  __/ |_
    # |_| |_|\___| \_/\_/     \_/\_/ \__,_|_|_|\___|\__|

    if options.new and not isfile(options.wallet):  # Create new Ed25519 keypair
        signing_key, verifying_key = ed25519.create_keypair(entropy=urandom)
        with open(options.wallet, "w") as ff:
            ff.write(signing_key.to_ascii(encoding="base64").decode())
            ff.write("\n")
            ff.write(verifying_key.to_ascii(encoding="base64").decode())
            ff.write("\n")
        exit("New keypair saved into the {}".format(options.wallet))
    elif options.new and isfile(options.wallet):  # There's a wallet already
        exit("Wallet already exists!")


    #      _
    #  ___(_) __ _ _ __      _ __ ___   ___  ___ ___  __ _  __ _  ___
    # / __| |/ _` | '_ \    | '_ ` _ \ / _ \/ __/ __|/ _` |/ _` |/ _ \
    # \__ \ | (_| | | | |   | | | | | |  __/\__ \__ \ (_| | (_| |  __/
    # |___/_|\__, |_| |_|   |_| |_| |_|\___||___/___/\__,_|\__, |\___|
    #        |___/                                         |___/

    if options.sign and isfile(options.wallet):
        signing_key = read_signing_key(options.wallet)
        sig = signing_key.sign(options.message.encode(), encoding="base64")
        exit("The signature is:\t {}".format(sig.decode("ascii")))
    elif options.sign and not isfile(options.wallet):
        exit("SD Can't find wallet, use 'python wallet.py -n'")

    #       _               _            _
    #   ___| |__   ___  ___| | __    ___(_) __ _ _ __
    #  / __| '_ \ / _ \/ __| |/ /   / __| |/ _` | '_ \
    # | (__| | | |  __/ (__|   <    \__ \ | (_| | | | |
    #  \___|_| |_|\___|\___|_|\_\   |___/_|\__, |_| |_|
    #                                      |___/

    if options.check_sign:
        verifying_key = ed25519.VerifyingKey(options.pub_key, encoding="base64")

        try:
            verifying_key.verify(
                options.check_sign.encode(),
                options.message.encode(),
                encoding="base64"
            )
            exit("Valid signature!")
        except ed25519.BadSignatureError:
            exit("Invalid signature!")

    #                      _           _
    #   ___ _ __ ___  __ _| |_ ___    | |___  ___ __
    #  / __| '__/ _ \/ _` | __/ _ \   | __\ \/ / '_ \
    # | (__| | |  __/ (_| | ||  __/   | |_ >  <| | | |
    #  \___|_|  \___|\__,_|\__\___|    \__/_/\_\_| |_|

    if options.transaction and isfile(options.wallet):
        signing_key = read_signing_key(options.wallet)
        verifying_key = read_verifying_key(path=options.wallet)

        txn = {
            "sender" : verifying_key.to_ascii(encoding="base64").decode(),
            "receiver" : options.receiver,
            "amount" : options.amount,
            "data" : options.data,
            "timestamp" : int(time())
        }

        # To sign a message you need to be sure, that the bytes sequence is imutable
        # So it's better to sign not the JSON, but the values in immutable order
        # To specify an order, I sorted all the keys lexicographically
        keys_sequence = sorted(txn.keys())
        msg_to_sign = ";".join([str(txn[k]) for k in keys_sequence])
        txn["signature"] = signing_key.sign(msg_to_sign.encode(), encoding="base64").decode("ascii")

        print ("Your txn is printed bellow. Copy as it is and send with the ABCI query\n")
        exit('0x' + hexlify((dumps(txn).encode())).decode('utf-8'))

    elif options.transaction and not isfile(options.wallet):
        exit("FFF Can't find wallet, use 'python wallet.py -n'")

    #  ___  ___ _ __   __| |   | |___  ___ __
    # / __|/ _ \ '_ \ / _` |   | __\ \/ / '_ \
    # \__ \  __/ | | | (_| |   | |_ >  <| | | |
    # |___/\___|_| |_|\__,_|    \__/_/\_\_| |_|

    if options.broadcast:
        r = requests.get("http://localhost:46657/broadcast_tx_async?tx={}".format(options.broadcast))

        if r.status_code == 200:
            txn_hash = r.json()['result']['hash'])
            exit("Txn broadcasted, txn hash: {txn_hash}".format(txn_hash)
        else:
            error_log = r.json()['result']['log'])
            exit("Can't broadcast your txn: {error_log}".format(error_log)

    #   __ _  ___| |_    | |__   __ _| | __ _ _ __   ___ ___
    #  / _` |/ _ \ __|   | '_ \ / _` | |/ _` | '_ \ / __/ _ \
    # | (_| |  __/ |_    | |_) | (_| | | (_| | | | | (_|  __/
    #  \__, |\___|\__|   |_.__/ \__,_|_|\__,_|_| |_|\___\___|
    #  |___/

    if options.get_balance:
        encoded_address = str(hexlify(options.get_balance.encode()), 'utf-8')

        # 0x62616c616e6365 = 'balance'
        r = requests.get("http://localhost:46657/abci_query?path=0x62616c616e6365&data=0x{}".format(encoded_address))

        if r.status_code == 200:
            encoded_balance = r.json()['result']['response']['value']

            exit("There are {amount} SimpleCoins on the {address}".format(
                amount=int.from_bytes(unhexlify(encoded_balance), byteorder='big'),
                address=options.get_balance
            ))
