from smache import Smache, Raw
from smache.schedulers import InProcessScheduler
from tests.helper import DummyA, DummyB, DummyC, redis_con
import pytest


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    DummyA.set_data({'1': {'value': 10}, '2': {'value': 500}})
    DummyB.set_data({'2': {'value': 20}})
    DummyC.set_data({'20': {'value': -1}, '30': {'value': -2}})
    yield


def setup_module(module):
    global smache, f, h

    DummyA.unsubscribe_all()
    DummyB.unsubscribe_all()
    DummyC.unsubscribe_all()

    smache = Smache(scheduler=InProcessScheduler())

    @smache.relations((DummyB, lambda b: DummyC.find('30')))
    @smache.computed(DummyA, DummyC, Raw, Raw)
    def f(a, dummyc, c, d):
        b = DummyB.find('2')
        return a.value * b.value

    @smache.relations((DummyB, lambda b: [DummyA.find('1'), DummyA.find('2')]))
    @smache.computed(DummyA, Raw, Raw)
    def h(a, c, d):
        b = DummyB.find('2')
        return a.value * b.value


def teardown_module(module):
    DummyA.unsubscribe_all()
    DummyB.unsubscribe_all()
    DummyC.unsubscribe_all()


def test_computed_function_are_updated_when_relations_are():
    ax = DummyA('1', 10)
    ax2 = DummyA('2', 500)
    cx = DummyC('20', 500)
    cx2 = DummyC('30', 500)

    assert f(ax, cx, 5, 10) == 200
    assert f(ax2, cx2, 5, 10) == 10000

    DummyC.update('30', {'value': 30})

    assert smache.is_fun_fresh(f, ax, cx, 5, 10) == True
    assert smache.is_fun_fresh(f, ax2, cx2, 5, 10) == False


def test_relations_with_list():
    ax = DummyA('1', 10)
    ax2 = DummyA('2', 500)

    assert h(ax, 5, 10) == 200
    assert h(ax2, 5, 10) == 10000

    DummyB.update('2', {'value': 30})

    assert smache.is_fun_fresh(h, ax, 5, 10) == False
    assert smache.is_fun_fresh(h, ax2, 5, 10) == False
