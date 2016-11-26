from smache import Smache
from smache.schedulers import InProcessScheduler
import pytest
import redis
import time

smache = Smache(scheduler=InProcessScheduler())
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@smache.computed(ttl=500)
def fun_with_ttl():
    return 50


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    smache._set_globals()
    redis_con.flushall()
    yield


def test_cached_values_are_not_updated_when_below_ttl(monkeypatch):
    key = smache.computed_key(fun_with_ttl, tuple())

    now = time.time()

    monkeypatch.setattr(time, 'time', lambda: now)

    smache._store.store(key, 100, 0)

    monkeypatch.setattr(time, 'time', lambda: now + 250)

    assert fun_with_ttl() == 100
    assert fun_with_ttl() == 100


def test_cached_values_are_updated_when_above_ttl(monkeypatch):
    key = smache.computed_key(fun_with_ttl, tuple())

    now = time.time()

    monkeypatch.setattr(time, 'time', lambda: now)

    smache._store.store(key, 100, 0)

    assert fun_with_ttl() == 100
    monkeypatch.setattr(time, 'time', lambda: now + 501)

    assert fun_with_ttl() == 100
    assert fun_with_ttl() == 50
