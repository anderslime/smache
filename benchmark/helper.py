import redis
from rq import Queue
from smache import Smache
from benchmark.db_helper import clean_dbs, connect_db_setup, User, Handin

# Setup
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)
worker_queue = Queue('test_queue', connection=redis_con)
smache = Smache(worker_queue=worker_queue, write_through=True)

@smache.computed(User, relations=[(Handin, lambda handin: handin.users)])
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
