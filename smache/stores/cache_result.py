import time


class CacheResult:
    def __init__(self, value, updated_at):
        self.value = value
        self.updated_at = updated_at

    def needs_refresh(self, ttl_in_seconds):
        return ttl_in_seconds is not None and \
            self.updated_at + ttl_in_seconds < time.time()
