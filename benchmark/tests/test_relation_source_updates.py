import benchmark.helper as helper

def make_underlying_data_change():
    handin = helper.Handin.objects.first()
    handin.save()

def run_benchmark(db_alias, benchmark):
    benchmark.pedantic(make_underlying_data_change,
                       setup=helper.connect_db_setup(db_alias),
                       iterations=1,
                       rounds=4)

def setup_module():
    helper.clean_dbs()

def test_relation_updates_with_db_small(benchmark):
    run_benchmark('small', benchmark)

def test_relation_updates_with_db_medium(benchmark):
    run_benchmark('medium', benchmark)

def test_relation_updates_with_db_large(benchmark):
    run_benchmark('large', benchmark)

def test_relation_updates_with_db_humongous(benchmark):
    run_benchmark('humongous', benchmark)
