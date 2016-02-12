from smache import Smache
from smache.data_sources.dummy_data_source import DummyEntity, DummyDataSource
from smache.function_serializer import FunctionSerializer

import redis

# Definitions
smache = Smache()
a = DummyDataSource('A')
b = DummyDataSource('B')

smache.add_sources(a, b)

@smache.computed(a, b)
def score(a, b, static):
    return (a.value + b.value) * static

def test_serialization():
    ax = DummyEntity(1, 10)
    bx = DummyEntity('2', 2)

    fun_serializer = FunctionSerializer(None)

    expected_serialization = '"score"~~~1~~~"2"~~~500'

    serialized_fun = fun_serializer.serialized_fun([a, b], score, ax, bx, 500)
    assert serialized_fun == expected_serialization

def test_deserialization():
    ax = DummyEntity(1, 10)
    bx = DummyEntity("2", 2)

    fun_serializer = FunctionSerializer(None)

    key = '"score"~~~1~~~"2"~~~500'

    fun_name, deserialized_args = fun_serializer.deserialized_fun(key)
    # first_arg = deserialized_args[0]
    # second_arg = deserialized_args[1]
    # third_arg = deserialized_args[2]

    assert fun_name == "score"
    assert deserialized_args == [1, '2', 500]
    # assert first_arg.value == 10
    # assert first_arg.id == 1
    # assert second_arg.value == 2
    # assert second_arg.id == 2
    # assert third_arg == 500
