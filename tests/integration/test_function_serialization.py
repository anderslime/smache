from smache import Smache
from smache.data_sources import DummyDataSource, RawDataSource, Raw
from smache.function_serializer import FunctionSerializer
from tests.helper import DummyA, DummyB

# Definitions
smache = Smache()
smache.add_sources(DummyA, DummyB, Raw)


@smache.computed(DummyA, DummyB, Raw)
def score(a, b, static):
    return (a.value + b.value) * static


@smache.computed(sources=(DummyA, DummyB))
def no_args():
    return "NO ARG IS FUN"


def test_serialization():
    ax = DummyA(1, 10)
    bx = DummyB('2', 2)

    fun_serializer = FunctionSerializer()

    a = DummyDataSource(DummyA)
    b = DummyDataSource(DummyB)
    raw = RawDataSource()

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
