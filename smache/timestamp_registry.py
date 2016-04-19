class TimestampRegistry:
    def __init__(self, redis_con):
        self._redis_con = redis_con

    def state_timestamp(self, key):
        return self._redis_con.get(self._state_ts_key(key))

    def value_timestamp(self, key):
        return self._redis_con.get(self._value_ts_key(key))

    def next_timestamp(self, key):
        redis_key = 'smache:timestamp:next:{}'.format(key)
        return self._redis_con.incr(redis_key)

    def _state_ts_key(self, key):
        return 'smache:timestamp:state:{}'.format(key)

    def _value_ts_key(self, key):
        return 'smache:timestamp:value:{}'.format(key)
