import redis
from rq import Queue
from smache import Smache, Raw
from benchmark.db_helper import clean_dbs, connect_db, connect_db_setup, User, Handin
import time

# Setup
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)
worker_queue = Queue('test_queue', connection=redis_con)
smache = Smache(worker_queue=worker_queue, write_through=True)

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
