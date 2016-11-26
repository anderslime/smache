class CacheResult:
    def __init__(self, value, updated_at, ttl):
        self.value = value
        self.updated_at = updated_at
        self.ttl = ttl
