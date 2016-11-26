import time
from smache.stores.cache_result import CacheResult


def test_need_refresh(monkeypatch):
    now = time.time()

    monkeypatch.setattr(time, 'time', lambda: now)

    cache_result = CacheResult('value', now)

    assert cache_result.needs_refresh(1) == False

    monkeypatch.setattr(time, 'time', lambda: now + 1.1)

    assert cache_result.needs_refresh(1) == True
