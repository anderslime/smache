import redis
from rq import Queue
from smache import Smache, Raw
from benchmark.db_helper import clean_dbs, connect_db, connect_db_setup, User, Handin
import time

# Setup
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)
worker_queue = Queue('test_queue', connection=redis_con)
smache = Smache(worker_queue=worker_queue)

@smache.relations((Handin, lambda handin: handin.users))
@smache.computed(User, Raw)
def score(user, sleep_time):
    handins = Handin.objects(users=user)
    time.sleep(sleep_time)
    total_score = sum(handin.score for handin in handins)
    avg_score = total_score / len(handins) if len(handins) > 0 else 0
    return {
        'name': user.name,
        'age': user.age,
        'total_score': total_score,
        'avg_score': avg_score
    }

@smache.computed(User, Raw)
def simple_slow_fun(user, variation):
    time.sleep(0.4)
    return "SIMPLE SLOW FUN"


## Cached functions to test nested computations


@smache.computed(User, Raw)
def eighth_layer(user, duration):
    time.sleep(duration)
    return seventh_layer(user, duration)

@smache.computed(User, Raw)
def seventh_layer(user, duration):
    time.sleep(duration)
    return sixth_layer(user, duration)


@smache.computed(User, Raw)
def sixth_layer(user, duration):
    time.sleep(duration)
    return fifth_layer(user, duration)


@smache.computed(User, Raw)
def fifth_layer(user, duration):
    time.sleep(duration)
    return fourth_layer(user, duration)


@smache.computed(User, Raw)
def fourth_layer(user, duration):
    time.sleep(duration)
    return third_layer(user, duration)


@smache.computed(User, Raw)
def third_layer(user, duration):
    time.sleep(duration)
    return second_layer(user, duration)


@smache.computed(User, Raw)
def second_layer(user, duration):
    time.sleep(duration)
    return first_layer(user, duration)


@smache.computed(User, Raw)
def first_layer(user, duration):
    time.sleep(duration)
    return "RESULT"
