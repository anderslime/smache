import redis
from rq import Queue
from smache import Smache, MongoDataSource
from tests.mongo_helper import User, Handin
from benchmark.db_helper import clean_and_connect_db

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

def make_underlying_data_change():
    user = User.objects.first()
    user.save()

def run_benchmark(db_name, benchmark):
    def setup():
        clean_and_connect_db(db_name)
    benchmark.pedantic(make_underlying_data_change,
                       setup=setup,
                       iterations=1,
                       rounds=4)

def test_relation_updates_with_db_small(benchmark):
    run_benchmark('small', benchmark)

def test_relation_updates_with_db_medium(benchmark):
    run_benchmark('medium', benchmark)

def test_relation_updates_with_db_large(benchmark):
    run_benchmark('large', benchmark)

def test_relation_updates_with_db_humongous(benchmark):
    run_benchmark('humongous', benchmark)
