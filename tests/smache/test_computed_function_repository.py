import pytest

from smache.function_serializer import FunctionSerializer
from smache.computed_function_repository import ComputedFunctionRepository
from smache.computed_function import ComputedFunction


def fun_fun():
    pass


def fun_not_added():
    pass


@pytest.yield_fixture
def computed_repo():
    serializer = FunctionSerializer()
    yield ComputedFunctionRepository(serializer)


@pytest.yield_fixture
def computed_fun():
    yield ComputedFunction(fun_fun, [], [], [])


def test_get_computed_function_from_function(computed_repo, computed_fun):
    computed_repo.add(computed_fun)

    assert computed_repo.get(fun_fun) == computed_fun

    with pytest.raises(KeyError):
        computed_repo.get(fun_not_added)


def test_get_computed_function_from_id(computed_repo, computed_fun):
    computed_repo.add(computed_fun)

    fun_id = 'test_computed_function_repository/fun_fun'

    assert computed_repo.get_from_id(fun_id) == computed_fun

    with pytest.raises(KeyError):
        computed_repo.get_from_id('not_existing_fun')


def test_computed_key_is_build_from_serializer(monkeypatch, computed_fun):
    serializer = FunctionSerializer()
    computed_repo = ComputedFunctionRepository(serializer)

    computed_repo.add(computed_fun)

    serialized_fun = 'my_serialized_fun'
    monkeypatch.setattr(serializer, 'serialized_fun',
                        lambda a, b: serialized_fun)

    assert computed_repo.computed_key(fun_fun, []) == serialized_fun
