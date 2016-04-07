class TimestampRegistry:
    def __init__(self, redis_con):
        self._redis_con = redis_con

    def next_timestamp(self, key):
        return self._redis_con.incr(self._timestamp_key(key))

    def _timestamp_key(self, key):
        return 'smache:timestamp:{}'.format(key)
