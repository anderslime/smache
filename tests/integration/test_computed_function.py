# Heloo
from smache.computed_function import ComputedFunction
from smache.data_sources.dummy_data_source import DummyEntity
from smache.data_sources import DummyDataSource, RawDataSource

a = DummyDataSource('A', {1: {'value': 10}})
b = DummyDataSource('B')

raw = RawDataSource()


def score(a, raw_value):
    return a.value + raw_value


def test_computed_function():
    computed_fun = ComputedFunction(score, (a, raw), (b), tuple())
    ax = DummyEntity(a.data_source_id, 1, 10)

    assert computed_fun(ax, 500) == 510
