import benchmark.helper as helper

def make_underlying_data_change(no_of_updates):
    def run_changes():
        for i in range(no_of_updates):
            handin = helper.Handin.objects.first()
            handin.score = i
            handin.save()
    return run_changes

def run_benchmark(db_alias, benchmark, no_of_updates):
    benchmark.pedantic(make_underlying_data_change(no_of_updates),
                       setup=helper.connect_db_setup(db_alias),
                       iterations=1,
                       rounds=4)

def setup_module():
    helper.clean_dbs()

def test_relation_updates_with_db_small_and_50_updates(benchmark):
    run_benchmark('small', benchmark, 50)

def test_relation_updates_with_db_small_and_100_updates(benchmark):
    run_benchmark('small', benchmark, 100)

def test_relation_updates_with_db_small_and_200_updates(benchmark):
    run_benchmark('small', benchmark, 200)

def test_relation_updates_with_db_medium_and_50_updates(benchmark):
    run_benchmark('medium', benchmark, 50)

def test_relation_updates_with_db_medium_and_100_updates(benchmark):
    run_benchmark('medium', benchmark, 100)

def test_relation_updates_with_db_medium_and_200_updates(benchmark):
    run_benchmark('medium', benchmark, 200)

# def test_relation_updates_with_db_large(benchmark):
#     run_benchmark('large', benchmark)
#
# def test_relation_updates_with_db_humongous(benchmark):
#     run_benchmark('humongous', benchmark)
