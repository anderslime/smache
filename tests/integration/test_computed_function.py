# Heloo
from smache.computed_function import ComputedFunction
from smache.data_sources.dummy_data_source import DummyEntity
from smache.data_sources import DummyDataSource, RawDataSource


class DummyA(DummyEntity):
    data = {1: {'value': 10}}


class DummyB(DummyEntity):
    pass


def score(a, raw_value):
    return a.value + raw_value


def test_computed_function():
    a = DummyDataSource(DummyA)
    b = DummyDataSource(DummyB)
    raw = RawDataSource()

    computed_fun = ComputedFunction(score, (a, raw), (b), tuple())
    ax = DummyA(1, 10)

    assert computed_fun(ax, 500) == 510
