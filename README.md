# SMache

[![Build Status](https://travis-ci.org/anderslime/smache.svg?branch=master)](https://travis-ci.org/anderslime/smache)

Smache is a Python library that allows you to cache the results of a
function and keep the values updated such that when the result is cached once,
you will never have to wait for the result to be computed since Smache will
automatically update your cached value when the underlying data updates.

## Setup

Smache uses Redis to store metadata about the cached functions, which means it
requires a connection to Redis. If you have Redis installed on you machine,
Smache will automatically use a default localhost connection.

With Redis installed, you have to install smache, e.g. using `pip`:

`pip install smache`

(Need documentation about the configuration possibilities)


## Usage

Smache is implemented using decorators, which means you don't need to change
the function in order to cache it. You only need to specify the dependencies of
your cached function. At the current moment Smache only works with MongoDB.

We will use an example to demonstrate the usage. The code for the examples are
also located in the `example`-folder.

Before using smache, we have an application in the `app.py` module with the
following code:

```python
import time
from mongoengine import Document, StringField, connect

connect('smache_test_db')

class User(Document):
  name = StringField()

def computed_value(user):
  time.sleep(2)  # To simulate slow computation
  return user.name
```

Since the function `computed_value` takes 2 seconds to compute, we would like
to cache it using smache.

We will therefore change our application, by instantiating a configured `Smache`
object and add a decorator to our function as following:

```python
import time
from mongoengine import Document, StringField, connect
from smache import Smache

connect('smache_test_db')

class User(Document):
  name = StringField()

mysmachecache = Smache()

@mysmachecache.computed(User)
def computed_value(user):
  time.sleep(2)  # To simulate slow computation
  return user.name
```

Smache updates cached values asynchronously, which means you need to start a
worker. To manage the background jobs, Smache uses [rq](http://python-rq.org/).

We need to run a worker in the same context as our application. As a simple example,
we can add the following code into a module called `worker.py`:

```python
import app

from rq import Connection, Worker, Queue

if __name__ == '__main__':
    with Connection():
        worker = Worker(Queue('smache'))
        worker.work()
```

To run the example, open up a terminal and run the worker:

```
python worker.py
```

To test that our app caches our value and updates it in the background, we
can run the following test (e.g. in a python terminal):

```python
import time
from app import User, computed_value

User(name='John Doe').save()

user = User.objects.order_by('-_id').first()

# This first time would take 4 seconds to compute
print computed_value(user)

user.name = 'John Dee'
user.save()

# At this point Smache has noticed that a cached value needs to be updated. We will wait a couple of seconds for it to finish.
time.sleep(4)

# This is computed instantly since it retreives the value from the cache
print computed_value(user)
```

## Tests

To run the tests, run:

`python setup.py test`

### Run tests continuously for development flow (OS X)

#### Setup

```
brew install terminal-notifier
python setup.py develop
pip install -rrequirements_dev.txt
```

#### Usage

```
./bin/watchtests
```
