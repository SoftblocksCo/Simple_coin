from redis import Redis

class DatabaseProvider(object):
    """docstring for DatabaseProvider."""
    def __init__(self, conf):
        self.conf = conf
        self.r = Redis(  # Connect to the Redis
            db=conf["redis"]["db"],
            decode_responses=True,
            host=conf["redis"]["host"],
            port=conf["redis"]["port"],
            password=conf["redis"]["pass"]
        )
        self.r.flushdb()

    def get_address_info(self, address):
        """Get all the data, assosiated with the address"""

        info = self.r.hgetall("state:{}".format(address))
        if 'balance' not in info:  # In case address has never appeared
            info['balance'] = 0

        return info

    def update_state(self, address=None, genesis=False, genesis_balance=None, tx=None):
        """Update state for some address"""

        if genesis:
            self.r.hmset('state:{}'.format(address), {"balance" : genesis_balance})
            return None

        # Process txn
        # - Update sender balance
        self.r.hincrby('state:{}'.format(tx.sender), "balance", -tx.amount)
        # - Update receiver balance
        self.r.hincrby('state:{}'.format(tx.receiver), "balance", tx.amount)

    def get_block_height(self):
        """Block height saved as an integer"""

        current_height = self.r.get("blockchain:height")

        if current_height is None:
            return 0
        return int(current_height)

    def set_block_height(self, height=None, increment=False):
        if increment:
            self.r.incr("blockchain:height")
        else:
            self.r.set("blockchain:height", height)

    def get_block_app_hash(self):
        """Latest block hash saved as a string"""

        current_hash = self.r.get("blockchain:app_hash")

        if current_hash is None:
            return ''
        return current_hash

    def set_block_app_hash(self, new_app_hash):
        """
            Used if new block has appeared. Save new hash
            instead of old one.
        """

        self.r.set("blockchain:app_hash", new_app_hash)
