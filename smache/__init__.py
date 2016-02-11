import redis

from stores import RedisStore
from dependency_graph import RedisDependencyGraph
from cache_manager import CacheManager

redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

dep_graph = RedisDependencyGraph(redis_con)
store     = RedisStore(redis_con)
smache    = CacheManager(store, dep_graph)
