class InvalidTimestampException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TimestampRegistry:
    first_timestamp = 0

    def __init__(self, redis_con):
        self._redis_con = redis_con

    def state_timestamp(self, key):
        return self._get_timestamp_or_default(self._state_ts_key(key), 0)

    def value_timestamp(self, key):
        return self._get_timestamp_or_default(self.value_ts_key(key), None)

    def increment_state_timestamp(self, key):
        self._redis_con.incr(self._state_ts_key(key))

    def is_newer_value_timestamp(self, key, new_value_timestamp):
        current_timestamp = self.value_timestamp(key)
        return current_timestamp is None or \
            int(new_value_timestamp) > int(current_timestamp)

    def is_timestamps_syncronized(self, key):
        state_ts, value_ts = self._redis_con.mget(
            self._state_ts_key(key),
            self.value_ts_key(key)
        )
        return state_ts is not None and \
            (value_ts is None or state_ts == value_ts)

    def set_value_timestamp(self, pipe, key, timestamp):
        current_state_timestamp = self._redis_con.get(self._state_ts_key(key))

        if current_state_timestamp is None:
            pipe.set(self._state_ts_key(key), timestamp)

        elif timestamp > current_state_timestamp:
            msg = "given timestamp {} cannot be larger than state timestamp {}"
            raise InvalidTimestampException(
                msg.format(timestamp, current_state_timestamp)
            )

        pipe.set(self.value_ts_key(key), timestamp)

    def _get_timestamp_or_default(self, key, default):
        timestamp = self._redis_con.get(key)
        return self._timestamp_or_default(timestamp, default)

    def _timestamp_or_default(self, timestamp, default):
        if timestamp is not None:
            return timestamp
        else:
            return default

    def value_ts_key(self, key):
        return 'smache:timestamp:value:{}'.format(key)

    def _state_ts_key(self, key):
        return 'smache:timestamp:state:{}'.format(key)
