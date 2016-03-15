import redis
from rq import Queue
from smache import Smache, MongoDataSource
from tests.mongo_helper import User, Handin, db

import logging, sys


# Setup
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)
worker_queue = Queue('test_queue', connection=redis_con)
smache = Smache(worker_queue=worker_queue, write_through=True)

user   = MongoDataSource(User)
handin = MongoDataSource(Handin)

smache.add_sources(user, handin)

@smache.computed(user, relations=[(handin, lambda handin: handin.users)])
def score(user):
    handins = Handin.objects(users=user)
    total_score = sum(handin.score for handin in handins)
    avg_score = total_score / len(handins)
    return {
        'name': user.name,
        'age': user.age,
        'total_score': total_score,
        'avg_score': avg_score
    }

num_of_handins_per_user = 100

def build_setup(num_of_users):
    def data_setup():
        db.drop_database('testdb')

        users = [User(name='Anders', age=25) for _ in range(num_of_users)]
        User.objects.insert(users)
        saved_users = User.objects()

        handins = [Handin(users=[user], score=10) for user in saved_users for _ in range(num_of_handins_per_user)]
        Handin.objects.insert(handins)

        for user in saved_users:
            score(user)

    return data_setup

def make_underlying_data_change():
    print "USER"
    user = User.objects.first()
    user.save()
    logger.info("HELLO INFO")
    logger.debug("HELLO INFO")
    print "USER SAVED"


def run_benchmark(benchmark, num_of_users):
    benchmark.pedantic(make_underlying_data_change,
                        setup=build_setup(num_of_users),
                        iterations=1,
                        rounds=1)

def test_performance_10_users(benchmark):
    run_benchmark(benchmark, 1)
    assert False
