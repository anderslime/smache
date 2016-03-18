import redis
import pytest

from smache.dependency_graphs import RedisDependencyGraph

redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


def test_dependency_graph():
    deps = RedisDependencyGraph(redis_con)
    deps.add_dependency('A', '1', 'hello/world')
    deps.add_dependency('A', '1', 'foo/bar')
    deps.add_dependency('A', '2', 'soo/tar')
    deps.add_dependency('B', '1', 'lalala')
    deps.add_data_source_dependency('A', 'full')

    assert deps.values_depending_on('A', '1') == set(
        ['hello/world', 'foo/bar', 'full']
    )
    assert deps.values_depending_on('A', '2') == set(['soo/tar', 'full'])
    assert deps.values_depending_on('B', '1') == set(['lalala'])
