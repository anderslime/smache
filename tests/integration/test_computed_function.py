# Heloo
from smache.computed_function import ComputedFunction
from smache.data_sources.in_memory_data_source import InMemoryEntity
from smache.data_sources import InMemoryDataSource, RawDataSource


class DummyA(InMemoryEntity):
    data = {1: {'value': 10}}


class DummyB(InMemoryEntity):
    pass


def score(a, raw_value):
    return a.value + raw_value


def test_computed_function():
    a = InMemoryDataSource(DummyA)
    raw = RawDataSource()

    computed_fun = ComputedFunction(score, (a, raw))
    ax = DummyA(1, 10)

    assert computed_fun(ax, 500) == 510


def test_options():
    computed_fun = ComputedFunction(None, tuple(), ttl=30)

    assert computed_fun.ttl == 30
