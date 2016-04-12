from smache import Smache, Raw
from smache.schedulers import InProcessScheduler
from tests.helper import DummyA, DummyB, DummyC, redis_con
import pytest


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


def setup_module(module):
    global smache, score, h, f, with_raw
    DummyA.unsubscribe_all()
    DummyB.unsubscribe_all()
    DummyC.unsubscribe_all()

    smache = Smache(scheduler=InProcessScheduler())

    @smache.sources(DummyB, DummyC)
    @smache.computed(DummyA)
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


def teardown_module(module):
    DummyA.unsubscribe_all()
    DummyB.unsubscribe_all()
    DummyC.unsubscribe_all()


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
