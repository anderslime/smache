class TimestampRegistry:
    def __init__(self, redis_con):
        self._redis_con = redis_con

    def state_timestamp(self, key):
        return self._redis_con.get(self._state_ts_key(key))

    def value_timestamp(self, key):
        return self._redis_con.get(self.value_ts_key(key))

    def set_value_timestamp(self, pipe, key, timestamp):
        pipe.set(self.value_ts_key(key), timestamp)

    def watch_value_timestamp(self, pipe, key):
        pipe.watch(self.value_ts_key(key))

    def next_timestamp(self, key):
        redis_key = 'smache:timestamp:next:{}'.format(key)
        return self._redis_con.incr(redis_key)

    def value_ts_key(self, key):
        return 'smache:timestamp:value:{}'.format(key)

    def _state_ts_key(self, key):
        return 'smache:timestamp:state:{}'.format(key)

