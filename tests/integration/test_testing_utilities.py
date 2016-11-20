from smache import Smache
from smache.data_sources import MongoDataSource
from smache.schedulers import InProcessScheduler
from tests.mongo_helper import User, Handin, test_connect
from tests.helper import relation_detector, RelationMissingError  # NOQA
import pytest
import redis

# Definitions
test_connect()

smache = Smache(scheduler=InProcessScheduler(), write_through=False)


@smache.computed()
def score_with_missing_relations():
    handin = Handin.objects().first()
    handin.users[0]
    return 50


@smache.sources(User, Handin)
@smache.computed()
def score_with_sources():
    handin = Handin.objects().first()
    handin.users[0]
    return 50


@smache.relations(
    (User, lambda user: user),
    (Handin, lambda handin: handin.users)
)
@smache.computed()
def score_with_relations():
    handin = Handin.objects().first()
    handin.users[0]
    return 50


def teardown_module(module):
    for data_source in smache._data_sources:
        if isinstance(data_source, MongoDataSource):
            data_source.disconnect()


# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    smache._set_globals()
    redis_con.flushall()
    yield


def test_raising_exceptions_on_missing_subscriptions(relation_detector):  # NOQA
    users = [User(name='Anders', age=12) for _ in range(1)]

    inserted_users = User.objects.insert(users)

    handin = Handin(score=1, users=inserted_users)
    handin.save()

    with pytest.raises(RelationMissingError):
        with relation_detector(score_with_missing_relations):
            assert score_with_missing_relations() == 50


def test_no_exceptions_raised_with_all_subscriptions(relation_detector):  # NOQA
    users = [User(name='Anders', age=12) for _ in range(1)]

    inserted_users = User.objects.insert(users)

    handin = Handin(score=1, users=inserted_users)
    handin.save()

    with relation_detector(score_with_sources):
        assert score_with_sources() == 50

    with relation_detector(score_with_relations):
        assert score_with_relations() == 50
