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
