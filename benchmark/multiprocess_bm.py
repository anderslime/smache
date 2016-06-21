from multiprocessing import Process
from rq import SimpleWorker, Worker
import benchmark.helper as helper
import time

def start_worker(index):
    def _start_worker():
        worker = Worker([helper.worker_queue], connection=helper.redis_con)
        worker.work()
    return _start_worker


def start_worker_process(index):
    p = Process(target=start_worker(index))
    return p

def are_workers_done():
    workers_working = 0
    for worker in Worker.all(connection=helper.redis_con):
        if worker.get_current_job():
            workers_working = workers_working + 1
    if workers_working > 0:
        print "WE HAVE {} WORKERS WORKING".format(workers_working)
        return False
    else:
        return True

def is_queue_empty():
    is_empty = helper.worker_queue.is_empty()
    if is_empty:
        return True
    else:
        return False

def start_workers(num_of_workers):
    def _start_workers():
        processes = [start_worker_process(i) for i in range(num_of_workers)]
        for p in processes:
            p.start()
        while not helper.worker_queue.is_empty() or not are_workers_done():
            time.sleep(0.2)
        for p in processes:
            p.terminate()
    return _start_workers
