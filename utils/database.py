from redis import Redis

class DatabaseProvider(object):
    """docstring for DatabaseProvider."""
    def __init__(self, conf):
        self.conf = conf
        self.r = Redis(db=conf["redis"]["db"], decode_responses=True) # Connect to the Redis
        self.r.flushdb()

    def get_address_info(self, address):
        """Get all the data, assoiated with the address"""
        info = self.r.hgetall("state:{}".format(address))
        if 'balance' not in info:
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
        current_hash = self.r.get("blockchain:app_hash")

        if current_hash is None:
            return ''
        return current_hash

    def set_block_app_hash(self, new_app_hash):
        self.r.set("blockchain:app_hash", new_app_hash)
