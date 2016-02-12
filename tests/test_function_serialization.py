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

@smache.computed(sources=(a, b))
def no_args():
    return "NO ARG IS FUN"

def test_serialization():
    ax = DummyEntity(1, 10)
    bx = DummyEntity('2', 2)

    fun_serializer = FunctionSerializer()

    expected_serialization = '"score"~~~1~~~"2"~~~500'

    key = fun_serializer.serialized_fun([a, b], score, ax, bx, 500)
    assert key == expected_serialization

    assert fun_serializer.deserialized_fun(key) == ("score", [1, '2', 500])

def test_de_and_serialization_of_no_arg_fun():
    fun_serializer = FunctionSerializer()

    key = fun_serializer.serialized_fun([], score)
    assert key == '"score"'
    assert fun_serializer.deserialized_fun(key) == ("score", [])

