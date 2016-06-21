import benchmark.helper as helper
from benchmark.multiprocess_bm import start_workers


def setup_test(layer_fun):
    db_alias = 'medium'
    no_of_updates = 1
    seconds = 1
    no_of_computeds = 1

    def _setup():
        helper.connect_db(db_alias)
        user = helper.User.objects.first()

        for _ in range(no_of_computeds):
            layer_fun(user, seconds)

        for i in range(no_of_updates):
            handin = helper.User.objects.first()
            handin.name = str(i)
            handin.save()

    return _setup


def run_benchmark(benchmark, layer_fun, no_of_workers):
    benchmark.pedantic(start_workers(no_of_workers),
                       setup=setup_test(layer_fun),
                       iterations=1,
                       rounds=1)


def setup_module():
    helper.clean_dbs()


def setup_function(fun):
    helper.redis_con.flushall()


def test_nested_updates_for_nested_computed_second_layer__workers_1(benchmark):
    run_benchmark(benchmark, helper.second_layer, 1)


def test_nested_updates_for_nested_computed_second_layer__workers_2(benchmark):
    run_benchmark(benchmark, helper.second_layer, 2)


def test_nested_updates_for_nested_computed_second_layer__workers_4(benchmark):
    run_benchmark(benchmark, helper.second_layer, 4)


def test_nested_updates_for_nested_computed_second_layer__workers_8(benchmark):
    run_benchmark(benchmark, helper.second_layer, 8)


def test_nested_updates_for_nested_computed_fourth_layer__workers_1(benchmark):
    run_benchmark(benchmark, helper.fourth_layer, 1)


def test_nested_updates_for_nested_computed_fourth_layer__workers_2(benchmark):
    run_benchmark(benchmark, helper.fourth_layer, 2)


def test_nested_updates_for_nested_computed_fourth_layer__workers_4(benchmark):
    run_benchmark(benchmark, helper.fourth_layer, 4)


def test_nested_updates_for_nested_computed_fourth_layer__workers_8(benchmark):
    run_benchmark(benchmark, helper.fourth_layer, 8)


def test_nested_updates_for_nested_computed_eighth_layer__workers_1(benchmark):
    run_benchmark(benchmark, helper.eighth_layer, 1)


def test_nested_updates_for_nested_computed_eighth_layer__workers_2(benchmark):
    run_benchmark(benchmark, helper.eighth_layer, 2)


def test_nested_updates_for_nested_computed_eighth_layer__workers_4(benchmark):
    run_benchmark(benchmark, helper.eighth_layer, 4)


def test_nested_updates_for_nested_computed_eighth_layer__workers_8(benchmark):
    run_benchmark(benchmark, helper.eighth_layer, 8)
