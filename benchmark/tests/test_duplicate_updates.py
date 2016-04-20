from rq import SimpleWorker
import benchmark.helper as helper

def execute_all_jobs(worker_queue, redis_con):
    worker = SimpleWorker([worker_queue], connection=redis_con)
    worker.work(burst=True)


def make_underlying_data_change(no_of_updates):
    def data_change():
        execute_all_jobs(helper.worker_queue, helper.redis_con)
    return data_change


def setup_test(db_alias, no_of_updates, run_time):
    def _setup():
        helper.connect_db(db_alias)
        user = helper.User.objects.first()
        helper.score(user, run_time)

        for i in range(no_of_updates):
            handin = helper.User.objects.first()
            handin.name = str(i)
            handin.save()

    return _setup


def run_benchmark(db_alias, benchmark, no_of_updates, run_time):
    benchmark.pedantic(make_underlying_data_change(no_of_updates),
                       setup=setup_test(db_alias, no_of_updates, run_time),
                       iterations=1,
                       rounds=1)

def setup_module():
    helper.clean_dbs()


def setup_function(fun):
    helper.redis_con.flushall()


def test_duplicate_updates_by_runtime__milliseconds_100(benchmark):
    run_benchmark('medium', benchmark, 10, 0.1)


def test_duplicate_updates_by_runtime__milliseconds_500(benchmark):
    run_benchmark('medium', benchmark, 10, 0.5)


def test_duplicate_updates_by_runtime__milliseconds_1000(benchmark):
    run_benchmark('medium', benchmark, 10, 1)


def test_duplicate_updates_by_updates__updates_10(benchmark):
    run_benchmark('medium', benchmark, 10, 0.5)


def test_duplicate_updates_by_updates__updates_20(benchmark):
    run_benchmark('medium', benchmark, 20, 0.5)


def test_duplicate_updates_by_updates__updates_40(benchmark):
    run_benchmark('medium', benchmark, 40, 0.5)
