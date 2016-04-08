from smache import Smache, Raw
from smache.data_sources.dummy_data_source import DummyEntity
from smache.schedulers import InProcessScheduler

import pytest
import redis

# Definitions
smache = Smache(scheduler=InProcessScheduler())


class DummyA(DummyEntity):
    pass


class DummyB(DummyEntity):
    pass


class DummyC(DummyEntity):
    pass

smache.add_sources(DummyA, DummyB, DummyC, Raw)


@smache.computed(DummyA, sources=(DummyB, DummyC))
def score(a):
    return a.value + 5 + 10


@smache.computed(DummyB, DummyC)
def h(b, c):
    return b.value + c.value


@smache.computed(DummyA, DummyB, DummyC)
def f(a, b, c):
    return a.value * h(b, c)


@smache.computed(DummyA, DummyB, Raw)
def with_raw(a, b, static_value):
    return (a.value + b.value) * static_value

# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


def test_cache():

    ax = DummyA(1, 10)
    bx = DummyB(2, 2)
    cx = DummyC(3, 3)

    assert f(ax, bx, cx) == 50
    assert h(bx, cx) == 5
    assert score(ax)

    assert smache.is_fun_fresh(score, ax) == True
    assert smache.is_fun_fresh(f, ax, bx, cx) == True
    assert smache.is_fun_fresh(h, bx, cx) == True

    DummyB.update(0, {})

    assert smache.is_fun_fresh(score, ax) == False
    assert smache.is_fun_fresh(f, ax, bx, cx) == True
    assert smache.is_fun_fresh(h, bx, cx) == True

    DummyA.update(1, {})

    assert smache.is_fun_fresh(score, ax) == False
    assert smache.is_fun_fresh(f, ax, bx, cx) == False
    assert smache.is_fun_fresh(h, bx, cx) == True

    DummyB.update(2, {})

    assert smache.is_fun_fresh(score, ax) == False
    assert smache.is_fun_fresh(f, ax, bx, cx) == False
    assert smache.is_fun_fresh(h, bx, cx) == False


def test_with_raw_value():
    ax = DummyA(1, 10)
    bx = DummyB(2, 2)

    assert with_raw(ax, bx, 1000) == 12000
