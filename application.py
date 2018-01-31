import struct
import utils

from random import randint
from binascii import hexlify

from abci import ABCIServer
from abci import BaseApplication
from abci import ResponseInfo
from abci import ResponseQuery
from abci import Result

from abci.types_pb2 import ResponseEndBlock
from abci.types_pb2 import ResponseBeginBlock

class SimpleCoin(BaseApplication):
    """
        Simple cryptocurrency implementation, based on the state model.
        Can do two things: sending coins and storing small pices of data
        in the blockchain.
    """

    def info(self):
        print ("INFO")
        """Called by ABCI when the app first starts."""

        self.conf = utils.read_conf()
        self.db = utils.DatabaseProvider(conf=self.conf)

        r = ResponseInfo()
        r.last_block_height = self.db.get_block_height()
        r.last_block_app_hash = self.db.get_block_app_hash().encode()
        return r
        print ("END INFO")

    def init_chain(self, v):
        """Set initial state on first run"""
        print ("INIT")

        for address, balance in self.conf['genesis']['lucky_bois'].items():
            self.db.update_state(
                address=address,
                genesis_balance=balance,
                genesis=True
            )

        self.db.set_block_height(0)
        self.db.set_block_app_hash('')
        print ("END INIT")

    def check_tx(self, raw_tx):
        """Validate the Tx before entry into the mempool"""
        print ("CHECK")

        try:  # Check txn syntax
            tx = utils.Transaction(raw_tx)
        except SyntaxError:
            return Result.error(log='txn syntax invalid')

        # Check "from" account has enough coins
        print (self.db.get_address_info(tx.sender))

        if self.db.get_address_info(tx.sender)['balance'] < tx.amount:
            return Result.error(log='not sufficient funds')

        if tx.signature_invalid:  # Check txn signature
            return Result.error(log='signature invalid')

        if tx.timestamp_invalid:  # Check timestamp for a big delay
            return Result.error(log='lag time is more than 2 hours')
        print ("END CHECK")

        # Hooray!
        return Result.ok()

    def deliver_tx(self, raw_tx):
        """ Mutate state if valid Tx """
        print ("DELIVER")

        try:  # Handle unvalid txn
            tx = utils.Transaction(raw_tx)
        except Exception as e:
            return Result.error(log='txn syntax invalid: {}'.format(e))

        self.new_block_txs.append(tx)
        self.db.update_state(tx=tx)
        print ("END DELIVER")

        return Result.ok()

    def query(self, reqQuery):
        """Return the last tx count"""
        if reqQuery.path == 'balance':
            address = reqQuery.data.decode('utf-8')
            address_balance = self.db.get_address_info(address)['balance']

            print (address, address_balance)

            rq = ResponseQuery(
                code=0,
                key=b'balance',
                value=utils.encode_number(int(address_balance))
            )

            return rq

    def begin_block(self, reqBeginBlock):
        """Called to process a block"""

        self.new_block_txs = []
        return ResponseBeginBlock()

    def end_block(self, height):
        """Called at the end of processing. If this is a stateful application
        you can use the height from here to record the last_block_height"""

        self.db.set_block_height(increment=True)
        self.db.set_block_app_hash(utils.get_merkle_root(self.new_block_txs))

        return ResponseEndBlock()

    def commit(self):
        """Return the current encode state value to tendermint"""

        h = self.db.get_block_app_hash().encode()

        return Result.ok(data=h)

if __name__ == '__main__':
    app = ABCIServer(app=SimpleCoin())
    app.run()
