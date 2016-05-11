import example.app  # NOQA

from rq import Connection, Worker, Queue

if __name__ == '__main__':
    with Connection():
        worker = Worker(Queue('smache'))
        worker.work()
