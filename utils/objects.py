from json import loads
from redis import Redis
from datetime import datetime

import ed25519
import hashlib

class Transaction(object):
    """This class is used for getting easy-to-use txn class
    from the bytes, received from the Tendermint core"""

    def __init__(self, tx):
        self.raw_tx = tx

        self.txn = loads(tx.decode())

        self.sender = self.txn["sender"]
        self.receiver = self.txn["receiver"]
        self.amount = self.txn["amount"]
        self.signature = self.txn["signature"]
        self.data = self.txn["data"]
        self.timestamp = self.txn["timestamp"]

        if len(self.txn.keys()) > 6:
            raise Exception("Unexpected key")

    def __repr__(self):
        return "From {}, To {}, Amount {}".format(self.sender, self.receiver, self.amount)

    @property
    def hash(self):
        """Get the transaction hash"""

        keys_sequence = sorted(self.txn.keys())
        msg_to_sign = ";".join([str(self.txn[k]) for k in keys_sequence])
        return hashlib.sha256(msg_to_sign.encode()).hexdigest()

    @property
    def signature_invalid(self):
        """Check if the signature corresponds to the """

        keys_sequence = sorted(self.txn.keys())
        msg_to_sign = ";".join([str(self.txn[k]) for k in keys_sequence])
        verifying_key = ed25519.VerifyingKey(self.sender, encoding="base64")

        try:
            verifying_key.verify(
                self.signature.encode(),
                msg_to_sign.encode(),
                encoding="base64"
            )
            return False
        except ed25519.BadSignatureError:
            return True

        return False

    @property
    def timestamp_invalid(self):
        current_datetime = datetime.now()
        txn_datetime = datetime.fromtimestamp(self.timestamp)

        return int(abs(current_datetime - txn_datetime) / 3600) > 2
