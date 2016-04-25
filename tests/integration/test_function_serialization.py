from smache import Smache
from smache.data_sources import InMemoryDataSource, RawDataSource, Raw
from smache.function_serializer import FunctionSerializer
from smache.computed_function import ComputedFunction
from tests.helper import DummyA, DummyB

# Definitions
smache = Smache()


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

    a = InMemoryDataSource(DummyA)
    b = InMemoryDataSource(DummyB)
    raw = RawDataSource()

    e = '"tests.integration.test_function_serialization/score"~~~1~~~"2"~~~500'

    computed_fun = ComputedFunction(score, [a, b, raw], [])

    key = fun_serializer.serialized_fun(computed_fun, ax, bx, 500)
    assert key == e

    expected_deserialization = (
        "tests.integration.test_function_serialization/score", [1, '2', 500]
    )
    assert fun_serializer.deserialized_fun(key) == expected_deserialization


def test_de_and_serialization_of_no_arg_fun():
    fun_serializer = FunctionSerializer()

    computed_fun = ComputedFunction(score, [], [])

    key = fun_serializer.serialized_fun(computed_fun)
    assert key == '"tests.integration.test_function_serialization/score"'
    assert fun_serializer.deserialized_fun(key) == (
        "tests.integration.test_function_serialization/score", []
    )
