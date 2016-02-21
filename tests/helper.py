from rq import SimpleWorker

def execute_all_jobs(worker_queue, redis_con):
    worker = SimpleWorker([worker_queue], connection=redis_con)
    worker.work(burst=True)
