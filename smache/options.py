import redis
from rq import Queue
from .schedulers import AsyncScheduler


class Options:
    defaults = {
        'write_through': False,
        'debug': False
    }

    def __init__(self, **options):
        self.options = self.defaults.update(options)

        self.write_through = self._value_equal(options, 'write_through', True)
        self.debug = self._value_equal(options, 'debug', True)
        self.redis_con = self._redis_con(options)
        self.worker_queue = self._worker_queue(options, self.redis_con)
        self.scheduler = self._scheduler(options, self.worker_queue)

    def _worker_queue(self, options, redis_con):
        return self._use_or_default(
            options.get('worker_queue'),
            lambda: Queue('smache', connection=redis_con)
        )

    def _redis_con(self, options):
        return self._use_or_default(
            options.get('redis_con'),
            lambda: redis.StrictRedis(host='localhost', port=6379, db=0)
        )

    def _scheduler(self, options, worker_queue):
        return self._use_or_default(
            options.get('scheduler'),
            lambda: AsyncScheduler(worker_queue)
        )

    def _use_or_default(self, value, default_lambda):
        if value is not None:
            return value
        else:
            return default_lambda()

    def _value_equal(self, options, prop, test_value):
        return prop in options and options[prop] == test_value
