from smache.data_sources.dummy_data_source import DummyEntity


class DummyA(DummyEntity):
    data = {'1': {'value': 10}, '2': {'value': 500}}


class DummyB(DummyEntity):
    data = {'2': {'value': 20}}

