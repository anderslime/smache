from smache import Smache
from smache.data_sources.dummy_data_source import DummyEntity
from smache.data_sources import DummyDataSource, RawDataSource
from smache.function_serializer import FunctionSerializer

# Definitions
smache = Smache()
a = DummyDataSource('A')
b = DummyDataSource('B')
raw = RawDataSource()

smache.add_sources(a, b, raw)


@smache.computed(a, b, raw)
def score(a, b, static):
    return (a.value + b.value) * static


@smache.computed(sources=(a, b))
def no_args():
    return "NO ARG IS FUN"


def test_serialization():
    ax = DummyEntity(a.data_source_id, 1, 10)
    bx = DummyEntity(b.data_source_id, '2', 2)

    fun_serializer = FunctionSerializer()

    e = '"tests.integration.test_function_serialization/score"~~~1~~~"2"~~~500'

    key = fun_serializer.serialized_fun([a, b, raw], score, ax, bx, 500)
    assert key == e

    expected_deserialization = (
        "tests.integration.test_function_serialization/score", [1, '2', 500]
    )
    assert fun_serializer.deserialized_fun(key) == expected_deserialization


def test_de_and_serialization_of_no_arg_fun():
    fun_serializer = FunctionSerializer()

    key = fun_serializer.serialized_fun([], score)
    assert key == '"tests.integration.test_function_serialization/score"'
    assert fun_serializer.deserialized_fun(key) == (
        "tests.integration.test_function_serialization/score", []
    )
