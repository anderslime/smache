class CacheResult:
    def __init__(self, value, updated_at, timeout_at):
        self.value = value
        self.updated_at = updated_at
        self.timeout_at = timeout_at
