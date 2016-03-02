import time, pytest

class MyBenchmark:
    def __init__(self):
        self.benchmarks = []
        self.append_stats = self.benchmarks.append

mybenchmark = MyBenchmark()

@pytest.fixture(scope="function")
def bm(benchmark):
    benchmark._add_stats = mybenchmark.append_stats
    return benchmark

@pytest.fixture(scope="function")
def bmstats():
    return mybenchmark

def hello():
    time.sleep(0.01)

def test_performance(bm, bmstats):
    bm.pedantic(hello, args=(), iterations=1, rounds=10)

    for bench in bmstats.benchmarks:
        print bench.stats.mean

    assert False
