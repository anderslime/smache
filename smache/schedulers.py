import smache
from .smache_logging import logger
from functools import reduce

from rq.job import Job
from rq.exceptions import NoSuchJobError


class AsyncScheduler:

    def __init__(self, worker_queue):
        self.worker_queue = worker_queue

    def schedule_write_through(self, keys):
        logger.debug("Schedule write through update on: {}".format(keys))
        reduce(self._enqueue_execute, keys, None)

    def schedule_update_handle(self, data_source_id, entity_id):
        logger.debug("Schedule update handle on update for: {}/{}".format(
            data_source_id,
            entity_id
        ))
        self.worker_queue.enqueue_call(
            func=_handle_data_source_update,
            args=(data_source_id, entity_id),
            at_front=True  # TODO: Use queue prioritization instead of this
        )

    def _enqueue_execute(self, last_job, key):
        existing_job = self._fetch_job(key)
        if existing_job and existing_job.is_queued:
            return
        return self.worker_queue.enqueue_call(
            func=_execute_from_key,
            args=(key,),
            job_id=key
        )

    def _fetch_job(self, key):
        try:
            return Job.fetch(key, connection=self.worker_queue.connection)
        except NoSuchJobError:
            return None


class InProcessScheduler:

    def schedule_write_through(self, keys):
        return [_execute_from_key(key) for key in keys]

    def schedule_update_handle(self, data_source_id, entity_id):
        _handle_data_source_update(data_source_id, entity_id)


def _handle_data_source_update(data_source_id, entity_id):
    smache._instance._data_update_propagator.handle_update(
        data_source_id,
        entity_id
    )


def _execute_from_key(key):
    logger.debug("EXECUTE on {}".format(key))

    computed_fun, args, kwargs = smache._instance.deserialized_fun(key)
    logger.debug("Calling computed function {} with args {}".format(
        computed_fun.fun.__name__,
        args
    ))
    if computed_fun.is_in_app_context():
        return execute_in_app(
            computed_fun.app,
            smache._instance._store,
            key,
            computed_fun,
            *args,
            **kwargs
        )
    else:
        return execute(
            smache._instance._store,
            key,
            computed_fun,
            *args,
            **kwargs
        )


def execute_in_app(app, store, key, computed_fun, *args, **kwargs):
    if store.is_fresh(key):
        return store.lookup(key).value
    else:
        with app.test_request_context('/'):
            with smache._instance.without_staleness():
                computed_value = computed_fun(*args)
                timestamp = \
                    smache._instance._timestamp_registry.state_timestamp(key)
                logger.debug("SMACHE: Storing new value for {}".format(key))
                store.store(key, computed_value, timestamp)
                return computed_value


def execute(store, key, computed_fun, *args, **kwargs):
    if store.is_fresh(key):
        return store.lookup(key).value
    else:
        with smache._instance.without_staleness():
            computed_value = computed_fun(*args, **kwargs)
            timestamp = \
                smache._instance._timestamp_registry.state_timestamp(key)
            logger.debug("SMACHE: Storing new value for {}".format(key))
            store.store(key, computed_value, timestamp)
            return computed_value
