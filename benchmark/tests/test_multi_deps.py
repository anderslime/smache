import benchmark.helper as helper
from benchmark.multiprocess_bm import start_workers


def setup_test(no_of_computeds):
    db_alias = 'medium'
    no_of_updates = 1
    # no_of_computeds = 50

    def _setup():
        helper.connect_db(db_alias)
        user = helper.User.objects.first()

        for i in range(no_of_computeds):
            helper.simple_slow_fun(user, i)

        for i in range(no_of_updates):
            handin = helper.User.objects.first()
            handin.name = str(i)
            handin.save()

    return _setup


def run_benchmark(benchmark, no_of_workers, no_of_computeds):
    benchmark.pedantic(start_workers(no_of_workers),
                       setup=setup_test(no_of_computeds),
                       iterations=1,
                       rounds=1)


def setup_module():
    helper.clean_dbs()


def setup_function(fun):
    helper.redis_con.flushall()


def test_nested_updates_for_umbrella_deps_10__workers_1(benchmark):
    run_benchmark(benchmark, 1, 10)


def test_nested_updates_for_umbrella_deps_10__workers_2(benchmark):
    run_benchmark(benchmark, 2, 10)


def test_nested_updates_for_umbrella_deps_10__workers_4(benchmark):
    run_benchmark(benchmark, 4, 10)


def test_nested_updates_for_umbrella_deps_10__workers_8(benchmark):
    run_benchmark(benchmark, 8, 10)


def test_nested_updates_for_umbrella_deps_20__workers_1(benchmark):
    run_benchmark(benchmark, 1, 20)


def test_nested_updates_for_umbrella_deps_20__workers_2(benchmark):
    run_benchmark(benchmark, 2, 20)


def test_nested_updates_for_umbrella_deps_20__workers_4(benchmark):
    run_benchmark(benchmark, 4, 20)


def test_nested_updates_for_umbrella_deps_20__workers_8(benchmark):
    run_benchmark(benchmark, 8, 20)


def test_nested_updates_for_umbrella_deps_40__workers_1(benchmark):
    run_benchmark(benchmark, 1, 40)


def test_nested_updates_for_umbrella_deps_40__workers_2(benchmark):
    run_benchmark(benchmark, 2, 40)


def test_nested_updates_for_umbrella_deps_40__workers_4(benchmark):
    run_benchmark(benchmark, 4, 40)


def test_nested_updates_for_umbrella_deps_40__workers_8(benchmark):
    run_benchmark(benchmark, 8, 40)


def test_nested_updates_for_umbrella_deps_80__workers_1(benchmark):
    run_benchmark(benchmark, 1, 80)


def test_nested_updates_for_umbrella_deps_80__workers_2(benchmark):
    run_benchmark(benchmark, 2, 80)


def test_nested_updates_for_umbrella_deps_80__workers_4(benchmark):
    run_benchmark(benchmark, 4, 80)


def test_nested_updates_for_umbrella_deps_80__workers_8(benchmark):
    run_benchmark(benchmark, 8, 80)
